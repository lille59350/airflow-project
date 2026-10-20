"""
Chargement des commandes CRM dans PostgreSQL.

Ce module réutilise :
- la connexion PostgreSQL existante ;
- le générateur de commandes synthétiques.
"""

# Réutiliser la fonction de connexion PostgreSQL.
from scripts.data_generation.load_customers import connect_to_postgresql

# Importer notre générateur de commandes.
from scripts.data_generation.generate_crm_data import generate_orders


def load_orders(connection, orders: list[dict]) -> int:
    """
    Charge une liste de commandes CRM dans PostgreSQL.

    Paramètres :
        connection : connexion PostgreSQL déjà ouverte.
        orders : liste de dictionnaires représentant les commandes.

    Retour :
        Nombre de commandes réellement insérées.
    """

    # Compteur des commandes insérées.
    inserted_count = 0

    # Requête SQL paramétrée pour insérer une commande.
    insert_query = """
        INSERT INTO public.orders (
            order_id,
            customer_id,
            order_date,
            status,
            currency,
            created_at,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO NOTHING
    """

    # Ouvrir un curseur PostgreSQL.
    with connection.cursor() as cursor:

        # Parcourir les commandes générées.
        for order in orders:

            # Exécuter la requête avec les valeurs de la commande.
            cursor.execute(
                insert_query,
                (
                    order["order_id"],
                    order["customer_id"],
                    order["order_date"],
                    order["status"],
                    order["currency"],
                    order["created_at"],
                    order["updated_at"],
                ),
            )

            # Compter uniquement les lignes réellement insérées.
            inserted_count += cursor.rowcount

    return inserted_count


def main() -> None:
    """
    Orchestre le chargement des commandes CRM.

    Étapes :
    1. Générer les commandes synthétiques.
    2. Ouvrir une connexion PostgreSQL.
    3. Insérer les commandes dans une transaction.
    4. Afficher le bilan du chargement.
    """

    # Générer les 10 commandes de notre jeu de test.
    orders = generate_orders(count=10, seed=42, start_id=3001)

    print(f"Commandes générées : {len(orders)}")

    # La connexion est utilisée comme contexte transactionnel :
    # succès = COMMIT ; exception = ROLLBACK.
    with connect_to_postgresql() as connection:

        # Insérer les commandes dans PostgreSQL.
        inserted_count = load_orders(connection, orders)

    # Ce message s'affiche après validation de la transaction.
    print(f"Commandes insérées : {inserted_count}")


# Point d'entrée du programme.
# main() est appelée uniquement si ce module
# est exécuté directement, et non lorsqu'il est importé.
if __name__ == "__main__":
    main()
