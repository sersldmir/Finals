import logging
import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



def main(env='test'):

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
        bind_address = "158.160.29.102"

    log.info(f"Env: {env}")

    log.info("Starting spark app")
    spark = (SparkSession.builder 
        .appName("Mark scoring data")
        .config("spark.log.level", "WARN")
        .config("spark.ui.bindAddress", bind_address)
        .config("spark.driver.bindAddress", bind_address)
        .master("yarn")
        .getOrCreate()
    )
    log.info("Spark app started")

    features_30_df = spark.read.orc("model_features_ml")

    feature_cols = [
        'age', 'gender_encoded', 'employment_status_encoded',
        'education_level_encoded', 'marital_status_encoded',
        'income_to_dependents_ratio', 'total_transaction_amount',
        'avg_transaction_amount', 'std_transaction_amount', 'transaction_count',
        'late_payment_ratio', 'avg_delinquency_days', 'max_delinquency_days',
        'total_loan_amount', 'avg_loan_amount', 'loan_count',
        'avg_interest_rate', 'remaining_balance_ratio']

    log.info("Vectorizing feats")
    assembler = VectorAssembler(
        inputCols=feature_cols,
        outputCol="features"
    )

    assembled_df = assembler.transform(features_30_df)

    log.info("Clustering feats")
    kmeans = KMeans(k=2, seed=777)
    kmeans_model = kmeans.fit(assembled_df)

    clustered_df = kmeans_model.transform(assembled_df).withColumnRenamed("prediction", "target")

    (
        clustered_df
        .drop('features', 'business_dt')
        .repartition(1)
        .write
        .orc("model_features_ml_marked", mode="overwrite")
    )

    log.info("Finished. Exiting...")
    spark.stop()


if __name__ == "__main__":
    main()