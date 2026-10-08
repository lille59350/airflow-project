from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

from pipeline_clients.transformation import transform_files
from pipeline_clients.extraction import extract_files
from pipeline_clients.quality import control_files
from pipeline_clients.loading import load_postgresql

with DAG(
    dag_id="pipeline_load_csv",
    start_date=datetime(2026, 9, 25),
    schedule=None,
    catchup=False,
) as dag:
    extract_task = PythonOperator(
        task_id="extract_files",
        python_callable=extract_files,
    )

    control_task = PythonOperator(
        task_id="control_files",
        python_callable=control_files,
    )

    transform_task = PythonOperator(
        task_id="transform_files",
        python_callable=transform_files,
    )

    load_task = PythonOperator(
        task_id="load_postgresql",
        python_callable=load_postgresql,
    )

    # Dépendance entre les deux tâches :
    # le contrôle intervient après l'extraction.
    extract_task >> control_task >> transform_task >> load_task
