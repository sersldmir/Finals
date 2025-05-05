from airflow import DAG
from airflow.providers.standard.operators.python import PythonVirtualenvOperator
from datetime import datetime
import os

os.environ['no_proxy']='*'

with open("requirements.txt") as file:
    reqs = file.readlines()

reqs = [i.replace('\n', '') for i in reqs]

if os.path.exists("./dev.txt"):
    env = "dev"
else:
    env = "test"

def generate_data(**kwargs):

    from scoring_modules import generate_data

    run_date = kwargs['logical_date'].strftime("%Y-%m-%d")

    generate_data.main(run_date=run_date, for_ml=True, env=env)

def agg_data(**kwargs):

    from scoring_modules import aggregate_data

    run_date = kwargs['logical_date'].strftime("%Y-%m-%d")

    aggregate_data.main(run_date=run_date, for_ml=True, env=env)

def mark_data():

    from scoring_modules import mark_data

    mark_data.main(env=env)

def teach_n_load():

    from scoring_modules import teach_n_load_model

    teach_n_load_model.main(env=env)



with DAG(
    'scoring_ml_dag',
    schedule='@once',
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=['scoring']
) as dag:
    

    generate_data_task = PythonVirtualenvOperator(
        task_id='generate_data',
        python_callable=generate_data,
        requirements=reqs,
        system_site_packages=False,
    )

    agg_data_task = PythonVirtualenvOperator(
        task_id='agg_data',
        python_callable=agg_data,
        requirements=reqs,
        system_site_packages=False,
    )

    mark_data_task = PythonVirtualenvOperator(
        task_id='mark_data',
        python_callable=mark_data,
        requirements=reqs,
        system_site_packages=False,
    )

    teach_n_load_task = PythonVirtualenvOperator(
        task_id='teach_n_load_model',
        python_callable=teach_n_load,
        requirements=reqs,
        system_site_packages=False,
    )

generate_data_task >> agg_data_task >> mark_data_task >> teach_n_load_task