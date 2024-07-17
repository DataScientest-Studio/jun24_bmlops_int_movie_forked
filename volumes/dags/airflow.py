from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow import DAG
from airflow.operators.python import PythonOperator

old_model_score = Variable.get(key="model_score")

with DAG(
    dag_id='data_model_pipeline',
    tags=['datascientest', 'project'],
    schedule_interval = '*/5 * * * *', # runs every 5 minutes
    start_date=days_ago(0),
    catchup=False,
    render_template_as_native_obj=True
) as my_dag:

    def preprocess_new_data():
        to_do = ""
    
    def load_processed_data_into_db():
        to_do = ""

    def retrain_model():
        to_do = ""

    def evaluate_new_model():
        to_do = ""

    def deploy_new_model():
        to_do = ""


    task_1 = PythonOperator(
        task_id='preprocess_new_data',
        python_callable=preprocess_new_data,
    )

    task_2 = PythonOperator(
        task_id='load_processed_data_into_db',
        python_callable=load_processed_data_into_db,
        op_kwargs={
            
        }
    )

    task_3 = PythonOperator(
        task_id='retrain_model',
        python_callable=retrain_model,
    )

    task_4 = PythonOperator(
        task_id='evaluate_new_model',
        python_callable=evaluate_new_model,
    )

    task_5 = PythonOperator(
        task_id='deploy_new_model',
        python_callable=deploy_new_model,
    )

task_1 >> task_2
task_2 >> task_3
task_3 >> task_4
task_4 >> task_5