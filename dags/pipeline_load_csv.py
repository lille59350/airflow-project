from airflow.sdk import DAG
from datetime import datetime
from pathlib import Path
import csv
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


def extract_files():
    """
    Vérifie que le fichier clients.csv est accessible
    depuis le conteneur Airflow qui exécute la tâche.
    """

    # Chemin du fichier vu depuis le conteneur Airflow.
    file_path = Path("/opt/airflow/data/clients.csv")

    # On vérifie que le fichier existe réellement.
    if not file_path.exists():
        raise FileNotFoundError(f"Le fichier source est introuvable : {file_path}")

    print(f"Fichier source trouvé : {file_path}")


def control_files():
    """
    Contrôle que le fichier clients.csv n'est pas vide.

    Cette première règle de qualité permet d'empêcher
    la suite du pipeline lorsqu'aucune donnée n'est disponible.
    """

    # Chemin du fichier dans le conteneur Airflow.
    file_path = Path("/opt/airflow/data/clients.csv")

    # On récupère la taille du fichier en octets.
    file_size = file_path.stat().st_size

    # Si la taille vaut 0, le fichier est complètement vide.
    if file_size == 0:
        raise ValueError(f"Le fichier est vide : {file_path}")

    print(f"Contrôle OK : {file_path} n'est pas vide " f"({file_size} octets).")

    # Liste des colonnes attendues dans le fichier source
    expected_columns = ["id_client", "nom", "prenom", "email"]

    # On ouvre le fichier csv en lecture
    with file_path.open("r", encoding="utf-8", newline="") as file:
        # DictReader interprète la première ligne comme les noms de colonnes.
        # Notre fichier utilise le point virgule comme séparateur.
        reader = csv.DictReader(file, delimiter=";")

        # On récupère les noms de colonnes réellement présents dans le fichier.
        actual_columns = reader.fieldnames

        print(f"Colonnes attendues : {expected_columns}")
        print(f"Colonnes recues : {actual_columns}")

        if actual_columns != expected_columns:
            raise ValueError(
                f"Structure du fichier incorrecte. "
                f"Attendu : {expected_columns}, reçu : {actual_columns}"
            )

        # Ensemble contenant les identifiants clients déjà rencontrés / IDs déjà rencontrés
        seen_ids = set()
        # duplicate_ids  → IDs identifiés comme doublons
        duplicate_ids = set()
        # Liste contenant les numéros des lignes dont l'id_client est vide
        missing_id_lines = []
        #
        quality_errors = []

        for line_number, row in enumerate(reader, start=2):
            id_client = row["id_client"].strip()

            print(f"Ligne {line_number} - ID client lu : {id_client}")

            # Si l'identifiant est vide, on mémorise la ligne concernée.
            if id_client == "":
                missing_id_lines.append(line_number)

                # On passe directement à la ligne suivante.
                # Une valeure vide ne doit pas participer au contrôle des doublons.
                continue

            # Si l'identifiant a déjà été rencontré,
            # on le mémorise comme doublon.
            if id_client in seen_ids:
                duplicate_ids.add(id_client)
            else:
                # Prémière occurence : on mémorise l'identifiant.
                seen_ids.add(id_client)

        print(f"Lignes avec id_client vide : {missing_id_lines}")

        if missing_id_lines:
            quality_errors.append(
                f"id_client obligatoire manquant aux lignes : {missing_id_lines}"
            )

        if duplicate_ids:
            quality_errors.append(
                f"Identifiants clients dupliqués : {sorted(duplicate_ids)}"
            )

        # Si au moins une anomalie a été détectée,
        # on construit un bilan global avant de faire échouer la tâche.
        if quality_errors:
            error_message = "Contrôle qualité échoué :\n- " + "\n- ".join(
                quality_errors
            )
            raise ValueError(error_message)


def transform_files():
    """
    Transforme les données clients après validation.

    Règle de transformation :
    - nom en majuscules ;
    - prénom avec la première lettre en majuscule;
    - email en minuscules.
    """

    source_path = Path("/opt/airflow/data/clients.csv")
    target_path = Path("/opt/airflow/data/clients_transformed.csv")

    with (
        source_path.open("r", encoding="utf-8", newline="") as source_file,
        target_path.open("w", encoding="utf-8", newline="") as target_file,
    ):
        reader = csv.DictReader(source_file, delimiter=";")
        writer = csv.DictWriter(
            target_file,
            fieldnames=reader.fieldnames,
            delimiter=";",
        )
        writer.writeheader()

        for row in reader:
            row["nom"] = row["nom"].strip().upper()
            row["prenom"] = row["prenom"].strip().capitalize()
            row["email"] = row["email"].strip().lower()

            writer.writerow(row)

            print(row)


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
