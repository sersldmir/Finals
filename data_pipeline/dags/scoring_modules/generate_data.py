import logging
import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import random
from datetime import date, timedelta, datetime

GENDERS = ['M', 'F', 'U']
EMPLOYMENT_STATUSES = ['employed', 'unemployed', 'self-employed', 'student', 'retired', 'unknown']
EDUCATION_LEVELS = ['none', 'primary', 'secondary', 'tertiary', 'postgraduate', 'unknown']
MARITAL_STATUSES = ['single', 'married', 'divorced', 'widowed', 'unknown']
TRANSACTION_TYPES = ['purchase', 'withdrawal', 'deposit', 'loan_payment', 'transfer', 'fee']
PAYMENT_STATUSES = ['on-time', 'late', 'missed', 'unknown']
LOAN_TYPES = ['mortgage', 'auto', 'personal', 'student', 'credit_card', 'business']
LOAN_STATUSES = ['active', 'closed', 'delinquent', 'default']

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

random.seed(datetime.now().timestamp())

def random_date(start_date, end_date):
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)


def generate_data(num_clients, num_transactions, num_loans):

    client_ids = [i+1 for i in range(num_clients)]
    random.shuffle(client_ids)

    transaction_ids = [i+1 for i in range(num_transactions)]
    random.shuffle(transaction_ids)

    loan_ids = [i+1 for i in range(num_loans)]
    random.shuffle(loan_ids)

    clients = []
    for client_id in client_ids:
        age = random.randint(18, 80)
        gender = random.choice(GENDERS)
        employment_status = random.choice(EMPLOYMENT_STATUSES)
        income = round(random.uniform(10000, 200000), 2)
        education_level = random.choice(EDUCATION_LEVELS)
        marital_status = random.choice(MARITAL_STATUSES)
        number_of_dependents = random.randint(0, 5)
        clients.append([client_id, age, gender, employment_status, income, education_level, marital_status, number_of_dependents])

    transactions = []
    for transaction_id in transaction_ids:
        client_id = random.choice(client_ids)
        transaction_date = random_date(date(2010, 1, 1), date.today())
        transaction_amount = round(random.uniform(10, 10000), 2)
        transaction_type = random.choice(TRANSACTION_TYPES)
        loan_id = random.choice(loan_ids) if transaction_type == 'loan_payment' else None
        payment_status = random.choice(PAYMENT_STATUSES)
        delinquency_days = random.randint(0, 90) if payment_status == 'late' else None
        transactions.append([transaction_id, client_id, transaction_date, transaction_amount, transaction_type, loan_id, payment_status, delinquency_days])

    loans = []
    for loan_id in loan_ids:
        client_id = random.choice(client_ids)
        loan_amount = round(random.uniform(1000, 500000), 2)
        loan_type = random.choice(LOAN_TYPES)
        loan_term = random.randint(1, 30) if loan_type in ['mortgage', 'auto', 'personal'] else random.randint(1, 10)
        interest_rate = round(random.uniform(2, 25), 2)
        start_date = random_date(date(2010, 1, 1), date.today())
        end_date = start_date + timedelta(days=loan_term*365)
        remaining_balance = round(loan_amount * (1 - random.uniform(0, 1)), 2)
        loan_status = random.choice(LOAN_STATUSES)
        loans.append([loan_id, client_id, loan_amount, loan_type, loan_term, interest_rate, start_date, end_date, remaining_balance, loan_status])

    return clients, transactions, loans


def main(for_ml=False, run_date=None, env='test'):

    if env == 'dev':
        os.environ['HADOOP_CONF_DIR'] = '/opt/homebrew/Cellar/hadoop/3.4.1/libexec/etc/hadoop'
        os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
        os.environ['JAVA_HOME'] = '/opt/homebrew/Cellar/openjdk@11/11.0.26/libexec/openjdk.jdk/Contents/Home'
        os.environ['no_proxy']='*'
    else:
        os.environ['SPARK_LOCAL_IP'] = '0.0.0.0'
        os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-11-openjdk-amd64'
        os.environ['HADOOP_CONF_DIR'] = '/home/sergmir/hadoop-3.4.1/etc/hadoop/'
        os.environ['no_proxy']='*'

    if run_date is None:
        run_date = datetime.now().strftime("%Y-%m-%d")

    log.info(f"Run date is {run_date}")

    log.info("Starting spark app")
    spark = (SparkSession.builder 
        .appName("Generate scoring data")
        .config("spark.log.level", "WARN")
        .config("spark.ui.bindAddress", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .master("yarn")
        .getOrCreate()
    )
    log.info("Spark app started")

    num_clients = random.randint(10_000, 30_000)
    num_transactions = random.randint(20_000, 50_000)
    num_loans = random.randint(5_000, 10_000)

    log.info(f"Generating data for {num_clients} clients, {num_transactions} transactions, {num_loans} loans")
    clients, transactions, loans = generate_data(num_clients, num_transactions, num_loans)
    log.info("Data generated, loading to Spark")

    clients_schema = ['client_id', 'age', 'gender', 'employment_status', 'income', 'education_level', 'marital_status', 'number_of_dependents']
    transactions_schema = ['transaction_id', 'client_id', 'transaction_date', 'transaction_amount', 'transaction_type', 'loan_id', 'payment_status', 'delinquency_days']
    loans_schema = ['loan_id', 'client_id', 'loan_amount', 'loan_type', 'loan_term', 'interest_rate', 'start_date', 'end_date', 'remaining_balance', 'loan_status']

    clinet_sdf = spark.createDataFrame(clients, schema=clients_schema)
    transactions_sdf = spark.createDataFrame(transactions, schema=transactions_schema)
    loans_sdf = spark.createDataFrame(loans, schema=loans_schema)

    log.info("Data received, saving to hdfs")

    if for_ml:
        write_mode = "overwrite"
        client_table = "clients_ml"
        transactions_table = "transactions_ml"
        loans_table = "loans_ml"
    else:
        write_mode = "append"
        client_table = "clients"
        transactions_table = "transactions"
        loans_table = "loans"


    (
        clinet_sdf
        .withColumn("business_dt", F.lit(run_date))
        .repartition(1)
        .write
        .partitionBy("business_dt")
        .orc(client_table, mode=write_mode)
    )

    (
        transactions_sdf
        .withColumn("business_dt", F.lit(run_date))
        .repartition(1)
        .write
        .partitionBy("business_dt")
        .orc(transactions_table, mode=write_mode)
    )

    (
        loans_sdf
        .withColumn("business_dt", F.lit(run_date))
        .repartition(1)
        .write
        .partitionBy("business_dt")
        .orc(loans_table, mode=write_mode)
    )

    log.info("Data saved! Exiting...")
    spark.stop()


if __name__ == "__main__":
    main()