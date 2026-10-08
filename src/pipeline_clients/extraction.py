from pathlib import Path


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
