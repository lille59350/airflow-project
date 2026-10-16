# DAG dédié au test d'atomicité PostgreSQL.
# il ne modifie pas la table métier "clients"

from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

# Réutilisation de notre véritable métier.
from pipeline_clients.loading import load_postgresql

with DAG(
    dag_id="test_atomicite_postgresql",
    start_date=datetime(2026, 10, 1),
    schedule=None,
    catchup=False,
    tags=["formation", "tests", "Postgresql"],
) as dag:

    test_rollback = PythonOperator(
        task_id="test_rollback",
        python_callable=load_postgresql,
        op_kwargs={
            "file_path": "/opt/airflow/data/clients_test_atomicite.csv",
            "table_name": "clients_test_atomicite",
        },
    )
