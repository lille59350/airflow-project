from pathlib import Path

# Construction sécurisée des requêtes SQL avec psycopg 3.
from psycopg import sql

import csv

from airflow.providers.postgres.hooks.postgres import PostgresHook

# src/pipeline_clients/loading.py : logique de chargement PostgreSQL.


def load_postgresql(
    file_path="/opt/airflow/data/clients_transformed.csv",
    table_name="clients",
):
    """
    Vérifie la connexion à la base PostgreSQL métier
    depuis une véritable tâche Airflow
    """

    # Le DAG connait uniquement l'identifiant logique de la connexion
    # les informations techniques sont stockées dans Airflow
    postgres_hook = PostgresHook(postgres_conn_id="postgres_metier")

    # Requête SQL permettant de créer la table cible.
    create_table_sql = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {} (
            id_client INTEGER PRIMARY KEY,
            nom VARCHAR(100),
            prenom VARCHAR(100),
            email VARCHAR(225)
            );
    """).format(sql.Identifier(table_name))

    # Exécute la requête SQL dans PostgreSQL.
    # postgres_hook.run(create_table_sql)

    # Création de la table dans une transaction distincte.
    create_connection = postgres_hook.get_conn()

    try:
        # Le curseur accepte notre requête SQL construite
        # avec sql.Identifier(table_name).
        with create_connection.cursor() as create_cursor:
            create_cursor.execute(create_table_sql)

        # Valide la création de la table.
        create_connection.commit()

    except Exception:
        # Annule la transaction de création en cas d'erreur.
        create_connection.rollback()
        raise

    finally:
        # Libère la connexion PostgreSQL.
        create_connection.close()

    print("Table clients disponible dans PostgreSQL")

    # Fichier produit par la tâche transform_files
    transformed_file_path = Path(file_path)

    # Transaction 2 : chargement atomique des clients.
    connection = postgres_hook.get_conn()
    connection.autocommit = False

    try:
        # Le curseur permet d'exécuter les requêtes SQL.
        with connection.cursor() as cursor:

            # Lecture du fichier transformé
            with transformed_file_path.open(
                "r",
                encoding="utf-8",
                newline="",
            ) as file:

                reader = csv.DictReader(file, delimiter=";")

                upsert_sql = sql.SQL("""
                INSERT INTO {} (id_client, nom, prenom, email)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id_client)
                DO UPDATE SET
                    nom = EXCLUDED.nom,
                    prenom = EXCLUDED.prenom,
                    email = EXCLUDED.email;
                """).format(sql.Identifier(table_name))

                # Tous les clients utilisent la même transaction.
                for row in reader:
                    parameters = (
                        row["id_client"],
                        row["nom"],
                        row["prenom"],
                        row["email"],
                    )

                    cursor.execute(upsert_sql, parameters)

        # Toutes les opérations ont réussi
        connection.commit()
        print("Chargement PostgreSQL validé : COMMIT")

    except Exception:
        # Une opération a échoué : annulation du lot
        connection.rollback()
        print("Echec du chargement : ROLLBACK")
        raise

    finally:
        # Libération de la connexion dans tous les cas
        connection.close()
