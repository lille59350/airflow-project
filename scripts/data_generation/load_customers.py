"""
NovaRetail CRM Data Platform
Chargement des clients synthétiques dans PostgreSQL.

Phase 3 - TP 3.2
"""

import os
import psycopg

from scripts.data_generation.generate_crm_data import generate_customers


def connect_to_postgresql():
    """
    Établit une connexion à la base PostgreSQL CRM source.

    Les identifiants sont lus depuis les variables
    d'environnement du conteneur Docker.
    """

    # Récupère les paramètres de connexion.
    host = os.environ.get("POSTGRES_HOST", "postgres-metier")
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    database = os.environ.get("POSTGRES_DB_SOURCE", "novaretail_crm_source")

    # Récupère les identifiants sans les afficher.
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]

    # Ouvre une connexion PostgreSQL avec Psycopg 3.
    connection = psycopg.connect(
        host=host,
        port=port,
        dbname=database,
        user=user,
        password=password,
        connect_timeout=5,
    )

    return connection


def load_customers(connection, customers: list[dict]) -> int:
    """
    Charge des clients synthétiques dans PostgreSQL.

    Règles :
    - Utiliser une requête SQL paramétrée.
    - Ignorer les identifiants déjà présents.
    - Retourner le nombre de clients réellement insérés.

    La transaction sera validée par le programme appelant.
    """

    # Requête d'insertion des clients.
    sql = """
        INSERT INTO public.customers (
            customer_id,
            first_name,
            last_name,
            email,
            country_code,
            created_at,
            updated_at
        )
        VALUES (
            %(customer_id)s,
            %(first_name)s,
            %(last_name)s,
            %(email)s,
            %(country_code)s,
            %(created_at)s,
            %(updated_at)s
        )
        ON CONFLICT (customer_id) DO NOTHING
    """

    inserted_count = 0

    # Le curseur permet d'exécuter les requêtes SQL.
    with connection.cursor() as cursor:

        # Chaque dictionnaire représente un client.
        for customer in customers:

            # Psycopg transmet les valeurs séparément du SQL.
            cursor.execute(sql, customer)

            # rowcount vaut 1 si la ligne a été insérée,
            # ou 0 si un conflit de clé primaire l'a empêchée.
            inserted_count += cursor.rowcount

    return inserted_count


def main():
    """
    Orchestre le chargement initial des clients synthétiques.

    La transaction est validée uniquement si toutes
    les opérations réussissent.
    """

    # Génère 100 clients fictifs de manière reproductible.
    customers = generate_customers(count=100, seed=42, start_id=1001)

    print(f"Clients générés : {len(customers)}")

    # Ouvre une connexion PostgreSQL.
    with connect_to_postgresql() as connection:

        # Charge les clients dans une seule transaction.
        inserted_count = load_customers(connection, customers)

        # Le gestionnaire de contexte valide la transaction
        # si aucune exception n'est survenue.
        # En cas d'erreur, il effectue un rollback.

    print(f"Clients réellement insérés : {inserted_count}")


if __name__ == "__main__":
    main()
