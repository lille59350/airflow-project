# ============================================================
# TEST D'ATOMICITÉ POSTGRESQL
# Objectif : vérifier qu'une erreur SQL entraîne un ROLLBACK
# et qu'aucune modification partielle n'est conservée.
# ============================================================

# Permet de créer une connexion PosgreSQL.
import psycopg2

# Permet de lire les paramètres de connexions depuis
# les variables d'environnement du conteneur
import os
