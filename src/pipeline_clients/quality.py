from pathlib import Path
import csv


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

        # Ensemble contenant les identifiants clients déjà rencontrés
        seen_ids = set()

        # IDs identifiés comme doublons
        duplicate_ids = set()

        # Numéros des lignes dont l'id_client est vide
        missing_id_lines = []

        # Liste regroupant les anomalies détectées
        quality_errors = []

        for line_number, row in enumerate(reader, start=2):
            id_client = row["id_client"].strip()

            print(f"Ligne {line_number} - ID client lu : {id_client}")

            # Si l'identifiant est vide, on mémorise la ligne concernée.
            if id_client == "":
                missing_id_lines.append(line_number)

                # Une valeur vide ne participe pas au contrôle des doublons.
                continue

            # Si l'identifiant a déjà été rencontré,
            # on le mémorise comme doublon.
            if id_client in seen_ids:
                duplicate_ids.add(id_client)
            else:
                # Première occurrence : on mémorise l'identifiant.
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
