import logging
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import DateType
from pyspark.ml.feature import StringIndexer
from pyspark.ml import Pipeline
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import os

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def main(for_ml=False, run_date=None, env='test'):

    if env == 'dev':
        os.environ['HADOOP_CONF_DIR'] = '/opt/homebrew/Cellar/hadoop/3.4.1/libexec/etc/hadoop'
        os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
        os.environ['JAVA_HOME'] = '/opt/homebrew/Cellar/openjdk@11/11.0.26/libexec/openjdk.jdk/Contents/Home'
        os.environ['no_proxy']='*'
        bind_address = "127.0.0.1"
    else:
        os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-11-openjdk-amd64'
        os.environ['HADOOP_CONF_DIR'] = '/home/sergmir/hadoop-3.4.1/etc/hadoop/'
        os.environ['no_proxy']='*'
        bind_address = "0.0.0.0"

    log.info(f"Env: {env}")

    if run_date is None:
        run_date = datetime.now().strftime("%Y-%m-%d")

    log.info(f"Run date is {run_date}")
    
    log.info("Starting spark app")
    spark = (SparkSession.builder 
        .appName("Aggregate scoring data")
        .config("spark.log.level", "WARN")
        .config("spark.ui.bindAddress", bind_address)
        .config("spark.driver.bindAddress", bind_address)
        .master("yarn")
        .getOrCreate()
    )
    log.info("Spark app started")

    if for_ml:
        write_mode = "overwrite"
        client_table = "clients_ml"
        transactions_table = "transactions_ml"
        loans_table = "loans_ml"
        target_table_name = "model_features_ml"
    else:
        write_mode = "append"
        client_table = "clients"
        transactions_table = "transactions"
        loans_table = "loans"
        target_table_name = "model_features"

    clinet_sdf = spark.read.orc(client_table)
    transactions_sdf = spark.read.orc(transactions_table)
    loans_sdf = spark.read.orc(loans_table)

    log.info("Filtering by 30 day time window")
    prediction_date_str = '2022-01-01'
    pred_date_col = F.lit(prediction_date_str).cast(DateType())
    window_30_days = F.date_sub(pred_date_col, 30)

    transactions_30_df = transactions_sdf.filter(
        (F.col('transaction_date').cast(DateType()) >= window_30_days) &
        (F.col('transaction_date').cast(DateType()) < pred_date_col)
    )

    loans_30_df = loans_sdf.filter(
        (F.col('start_date').cast(DateType()) < pred_date_col) &
        ((F.col('end_date').cast(DateType()) >= window_30_days) | F.col('end_date').isNull())
    )

    log.info("Aggregating trasaction feats")
    transaction_features = transactions_30_df.groupBy('client_id').agg(
        F.sum('transaction_amount').alias('total_transaction_amount'),
        F.mean('transaction_amount').alias('avg_transaction_amount'),
        F.stddev_samp('transaction_amount').alias('std_transaction_amount'),
        F.count('transaction_id').alias('transaction_count'),
        (F.sum(F.when(F.col('payment_status') == 'late', 1).otherwise(0)) / F.count('*')).alias('late_payment_ratio'),
        F.mean('delinquency_days').alias('avg_delinquency_days'),
        F.max('delinquency_days').alias('max_delinquency_days')
    )

    log.info("Aggregating loan feats")

    total_loan_amount_row = loans_30_df.select(F.sum('loan_amount').alias('total_loan_amount')).first()
    total_loan_amount = total_loan_amount_row['total_loan_amount'] if total_loan_amount_row['total_loan_amount'] is not None else 0.0

    safe_total_loan_amount = total_loan_amount if total_loan_amount != 0 else 1e-8

    loan_features = loans_30_df.groupBy('client_id').agg(
        F.sum('loan_amount').alias('total_loan_amount'),
        F.mean('loan_amount').alias('avg_loan_amount'),
        F.count('loan_id').alias('loan_count'),
        F.mean('interest_rate').alias('avg_interest_rate'),
        (F.sum('remaining_balance') / safe_total_loan_amount).alias('remaining_balance_ratio')
    )

    log.info("Aggregating client feats")

    category_cols = ['gender', 'employment_status', 'education_level', 'marital_status']
    indexers = [StringIndexer(inputCol=col, outputCol=f"{col}_encoded", handleInvalid="keep") for col in category_cols]


    pipeline = Pipeline(stages=indexers)
    clients_encoded_df = pipeline.fit(clinet_sdf).transform(clinet_sdf)

    client_features = clients_encoded_df.select(
        'client_id',
        'age',
        'gender_encoded',
        'employment_status_encoded',
        'income',
        'education_level_encoded',
        'marital_status_encoded',
        'number_of_dependents'
    )

    client_features = client_features.withColumn(
        'income_to_dependents_ratio',
        F.col('income') / (F.col('number_of_dependents') + 1)
    ).drop('income', 'number_of_dependents')

    log.info("Joining feats")
    model_features = (
        client_features
        .join(
            transaction_features, 
            on='client_id', 
            how='left')
        .join(
            loan_features, 
            on='client_id', 
            how='left')
    )

    log.info("Filling nulls")
    cols_to_fill = [
        col_name for col_name in model_features.columns
        if col_name != 'client_id' and not col_name.endswith('_encoded')
    ]

    for col_name in cols_to_fill:
        try:
            median = model_features.approxQuantile(col_name, [0.5], 0.01)[0]
            if median is not None:
                model_features = model_features.fillna({col_name: median})
        except Exception as e:
            print(f"Could not impute column '{col_name}': {str(e)}")

    log.info("Saving feats")
    (
        model_features
        .withColumn("business_dt", F.lit(run_date))
        .repartition(1)
        .write
        .partitionBy("business_dt")
        .orc(target_table_name, mode=write_mode)
    )

    if not for_ml:

        log.info("Loading metrics to grafana")

        row_count = model_features.select("client_id").count()
        row_distinct_count = model_features.select("client_id").distinct().count()

        features_metrics = [
            (run_date, row_count, row_distinct_count)
        ]

        try:
            connection = psycopg2.connect(
                dbname='scoring',
                user='postgres_dev',
                host=bind_address,
                port='5432'
            )

            cursor = connection.cursor()
            
            insert_features_dq_query = "INSERT INTO features_dq_metrics (business_dt, count_all, count_unique) VALUES %s"
            execute_values(cursor, insert_features_dq_query, features_metrics)
            connection.commit()

        except Exception as error:
            print("Error while connecting to db", error)

        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Db connection is closed")

    log.info("Finished. Exiting...")
    spark.stop()


if __name__ == "__main__":
    main()