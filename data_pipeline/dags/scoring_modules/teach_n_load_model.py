import logging
import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import mlflow
import mlflow.lightgbm
from mlflow.models import infer_signature


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
        bind_address = "0.0.0.0"
    
    log.info(f"Env: {env}")

    log.info("Starting spark app")
    spark = (SparkSession.builder 
        .appName("Score data and load to service")
        .config("spark.log.level", "WARN")
        .config("spark.ui.bindAddress", bind_address)
        .config("spark.driver.bindAddress", bind_address)
        .master("yarn")
        .getOrCreate()
    )
    log.info("Spark app started")

    log.info("Loading and splitting data")
    whole_train_df = spark.read.orc("model_features_ml_marked")

    df = (
        whole_train_df
        .drop("client_id")
        .toPandas()
    )

    spark.stop()

    y = df[['target']]
    X = df.drop(columns=['target'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=777)

    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

    params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'boosting_type': 'gbdt',
        'num_leaves': 27,
        'learning_rate': 0.05,
        'feature_fraction': 0.9,
        'is_unbalance': True
    }

    log.info("Training model")
    gbm = lgb.train(params, train_data, num_boost_round=100, valid_sets=[test_data])

    log.info("Testing model")
    y_pred_prob = gbm.predict(X_test, num_iteration=gbm.best_iteration)
    roc_auc = roc_auc_score(y_test, y_pred_prob)
    log.info(f'ROC AUC Score: {roc_auc}')

    log.info("Loading model to MLFlow")
    mlflow.set_tracking_uri(f"http://{bind_address}:8081")
    mlflow.set_experiment("LightGBM Classifier MLFlow demo + Spark")

    with mlflow.start_run():

        mlflow.log_params(params)

        mlflow.log_metric("roc_auc", roc_auc)

        signature = infer_signature(X_train, gbm.predict(X_train))

        mlflow.lightgbm.log_model(
            lgb_model=gbm,
            artifact_path="model",
            registered_model_name="lightgbm_classifier_spark_demo",
            signature=signature,
            input_example=X_train
        )

    log.info("Finished. Exiting...")


if __name__ == "__main__":
    main()