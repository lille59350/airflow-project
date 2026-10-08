from pathlib import Path
import csv

from airflow.providers.postgres.hooks.postgres import PostgresHook


def load_postgresql():
    """
    Vérifie la connexion à la base PostgreSQL métier
    depuis une véritable tâche Airflow
    """

    # Le DAG connait uniquement l'identifiant logique de la connexion
    # les informations techniques sont stockées dans Airflow
    postgres_hook = PostgresHook(postgres_conn_id="postgres_metier")

    # Requête SQL permettant de créer la table cible.
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS clients (
        id_client INTEGER PRIMARY KEY,
        nom VARCHAR(100),
        prenom VARCHAR(100),
        email VARCHAR(225)
    );
    """

    # Exécute la requête SQL dans PostgreSQL.
    postgres_hook.run(create_table_sql)

    print("Table clients disponible dans PostgreSQL")

    # Fichier produit par la tâche transform_files
    transformed_file_path = Path("/opt/airflow/data/clients_transformed.csv")

    with transformed_file_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=";")

        upsert_sql = """
        INSERT INTO clients (id_client, nom, prenom, email)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_client)
        DO UPDATE SET
            nom = EXCLUDED.nom,
            prenom = EXCLUDED.prenom,
            email = EXCLUDED.email;
        """
        for row in reader:
            print(f"Client à charger : {row}")

            parameters = (
                row["id_client"],
                row["nom"],
                row["prenom"],
                row["email"],
            )

            # Exécute l'UPSERT pour le client courant.
            postgres_hook.run(
                upsert_sql,
                parameters=parameters,
            )
