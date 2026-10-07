from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.git.hooks.git import GitHook

from datetime import datetime
import subprocess
import os


def test_git_connection():
    """
    Teste l'accès au dépôt Git distant en utilisant
    la connexion Airflow 'git_default'.
    """

    # Création du Hook à partir de la connexion Airflow / # Récupère la configuration de la connexion git_default.
    git_hook = GitHook(git_conn_id="git_default")

    # Prépare temporairement l'environnement Git/SSH :
    # clé SSH, known_hosts, passphrase, etc.
    with git_hook.configure_hook_env():

        # Exécute :
        # git ls-remote <URL_DU_DEPOT>
        result = subprocess.run(
            [
                "git",
                "ls-remote",
                git_hook.repo_url,
            ],
            env={**os.environ, **git_hook.env},
            capture_output=True,
            text=True,
        )

        print(f"Code retour Git : {result.returncode}")
        print(f"STDOUT Git : {result.stdout}")
        print(f"STDERR Git : {result.stderr}")

        if result.returncode != 0:
            raise RuntimeError(
                f"git ls-remote a échoué avec le code {result.returncode}"
            )


with DAG(
    dag_id="test_git_provider",
    start_date=datetime(2026, 9, 25),
    schedule=None,
    catchup=False,
) as dag:
    test_git_task = PythonOperator(
        task_id="test_git_connection",
        python_callable=test_git_connection,
    )
