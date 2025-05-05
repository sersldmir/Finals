from datetime import datetime
import logging
import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import mlflow
import psycopg2
from psycopg2.extras import execute_values
from pyspark.sql.types import DecimalType

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def main(run_date=None, env='test'):

    if env == 'dev':
        os.environ['HADOOP_CONF_DIR'] = '/opt/homebrew/Cellar/hadoop/3.4.1/libexec/etc/hadoop'
        os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
        os.environ['JAVA_HOME'] = '/opt/homebrew/Cellar/openjdk@11/11.0.26/libexec/openjdk.jdk/Contents/Home'
        os.environ['no_proxy']='*'
    else:
        os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-11-openjdk-amd64'
        os.environ['HADOOP_CONF_DIR'] = '/home/sergmir/hadoop-3.4.1/etc/hadoop/'
        os.environ['no_proxy']='*'

    log.info(f"Env: {env}")

    if run_date is None:
        run_date = datetime.now().strftime("%Y-%m-%d")

    log.info(f"Run date is {run_date}")

    log.info("Starting spark app")
    spark = (SparkSession.builder 
        .appName("Teach and load model")
        .config("spark.log.level", "WARN")
        .config("spark.ui.bindAddress", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.jars.packages", "org.postgresql:postgresql:42.2.18")
        .master("yarn")
        .getOrCreate()
    )
    log.info("Spark app started")

    log.info("Loading model from MLFlow")
    mlflow.set_tracking_uri("http://127.0.0.1:8081")

    model_name = "lightgbm_classifier_spark_demo"
    version = "latest"
    model_uri = f"models:/{model_name}/{version}"
    model_udf = mlflow.pyfunc.spark_udf(spark, model_uri=model_uri)

    features = ['age', 'gender_encoded', 'employment_status_encoded',
        'education_level_encoded', 'marital_status_encoded',
        'income_to_dependents_ratio', 'total_transaction_amount',
        'avg_transaction_amount', 'std_transaction_amount', 'transaction_count',
        'late_payment_ratio', 'avg_delinquency_days', 'max_delinquency_days',
        'total_loan_amount', 'avg_loan_amount', 'loan_count',
        'avg_interest_rate', 'remaining_balance_ratio']

    log.info("Scoring...")
    features_df = spark.read.orc("model_features").where(F.col("business_dt") == run_date)
    predicted_scores = features_df.withColumn("target", 
        model_udf(*features).getItem(0).cast(DecimalType(precision=15, scale=10))
    )

    log.info("Saving scores to hdfs")
    (
        predicted_scores
        .select("client_id", "business_dt", "target")
        .repartition(1)
        .write
        .partitionBy("business_dt")
        .orc("predicted_scores", mode="append")
    )

    log.info("Loading metrics to Grafana")
    
    count_all = predicted_scores.select('target').count()
    null_count = (
        predicted_scores
        .select('target')
        .filter(F.col("target").isNull())
        .count()
    )

    scoring_metrics = [
        (run_date, null_count/count_all, (count_all - null_count)/count_all)
    ]

    try:
        connection = psycopg2.connect(
            dbname='scoring',
            user='postgres_dev',
            host='localhost',
            port='5432'
        )

        cursor = connection.cursor()

        insert_scoring_dq_query = "INSERT INTO scores_dq_metrics (business_dt, count_null, count_not_null) VALUES %s"
        execute_values(cursor, insert_scoring_dq_query, scoring_metrics)
        connection.commit()

    except Exception as error:
        print("Error while connecting to db", error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Db connection is closed")
            

    log.info("Loading scores to db")

    db_url = "jdbc:postgresql://localhost:5432/scoring"
    db_properties = {
        "user": "postgres_dev",
        "password": "",
        "driver": "org.postgresql.Driver"
    }

    (
        predicted_scores
        .select("client_id", "target")
        .withColumnRenamed("client_id", "id")
        .withColumn("id", F.col("id").cast("string"))
        .withColumnRenamed("target", "score")
        .write
        .jdbc(url=db_url, table="scores_service", mode="overwrite", properties=db_properties)
    )



if __name__ == "__main__":
    main()