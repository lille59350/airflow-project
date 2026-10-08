from pathlib import Path
import csv


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
