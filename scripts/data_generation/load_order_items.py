"""
Chargement des lignes de commande synthétiques
dans PostgreSQL — NovaRetail CRM DATA PLATFORM.
"""

from scripts.data_generation.load_customers import connect_to_postgresql
from scripts.data_generation.generate_crm_data import generate_order_items


def load_order_items(connection, order_items: list[dict]) -> int:
    """
    Insère les lignes de commande dans PostgreSQL.

    Paramètres :
        connection : connexion PostgreSQL existante.
        order_items : liste de dictionnaires à charger.

    Retour :
        Nombre de lignes réellement insérées.
    """

    # Requête SQL paramétrée pour éviter de construire
    # du SQL directement à partir des valeurs Python.
    sql = """
        INSERT INTO public.order_items (
            order_item_id,
            order_id,
            product_id,
            quantity,
            unit_price,
            created_at,
            updated_at
        )
        VALUES (
            %(order_item_id)s,
            %(order_id)s,
            %(product_id)s,
            %(quantity)s,
            %(unit_price)s,
            %(created_at)s,
            %(updated_at)s
        )
        ON CONFLICT (order_item_id) DO NOTHING
    """

    inserted_count = 0

    # Le curseur exécute les instructions SQL.
    with connection.cursor() as cursor:

        # Chaque dictionnaire fournit les paramètres SQL.
        for order_item in order_items:
            cursor.execute(sql, order_item)

            # rowcount vaut 1 si la ligne est insérée,
            # ou 0 si son identifiant existe déjà.
            inserted_count += cursor.rowcount

    return inserted_count


def main():
    """Génère puis charge les lignes de commande."""

    order_items = generate_order_items(count=30, seed=42, start_id=4001)

    print(f"Lignes générées : {len(order_items)}")

    # La transaction est validée si tout réussit.
    # En cas d'erreur, elle est annulée automatiquement.
    with connect_to_postgresql() as connection:
        inserted_count = load_order_items(connection, order_items)

    print(f"Lignes insérées : {inserted_count}")


if __name__ == "__main__":
    main()
