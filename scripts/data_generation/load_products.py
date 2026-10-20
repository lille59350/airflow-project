"""
NovaRetail CRM Data Platform
Chargement des produits synthétiques dans PostgreSQL.

Phase 3 - TP 3.2
"""

# Fonction de connexion PostgreSQL déjà validée.
from scripts.data_generation.load_customers import connect_to_postgresql

# Générateur de produits synthétiques.
from scripts.data_generation.generate_crm_data import generate_products


def load_products(connection, products: list[dict]) -> int:
    """
    Charge les produits synthétiques dans PostgreSQL.

    Règles :
    - Utiliser des requêtes SQL paramétrées.
    - Ignorer les produits déjà présents.
    - Retourner le nombre de produits insérés.

    La transaction est gérée par le programme appelant.
    """

    # Requête SQL d'insertion dans la table products.
    sql = """
        INSERT INTO public.products (
            product_id,
            product_name,
            category,
            unit_price,
            currency,
            is_active,
            created_at,
            updated_at
        )
        VALUES (
            %(product_id)s,
            %(product_name)s,
            %(category)s,
            %(unit_price)s,
            %(currency)s,
            %(is_active)s,
            %(created_at)s,
            %(updated_at)s
        )
        ON CONFLICT (product_id) DO NOTHING
    """

    inserted_count = 0

    # Ouvrir un curseur pour exécuter les requêtes SQL.
    with connection.cursor() as cursor:

        # Parcourir chaque produit généré.
        for product in products:

            # Insérer le produit avec des paramètres sécurisés.
            cursor.execute(sql, product)

            # Compter uniquement les lignes réellement insérées.
            inserted_count += cursor.rowcount

    return inserted_count


def main():
    """
    Orchestre le chargement initial des produits synthétiques.

    La transaction est validée uniquement si toutes
    les insertions réussissent.
    """

    # Générer 10 produits fictifs reproductibles.
    products = generate_products(count=10, seed=42, start_id=2001)

    print(f"Produits générés : {len(products)}")

    # Ouvrir une connexion PostgreSQL.
    with connect_to_postgresql() as connection:

        # Insérer les produits dans une transaction.
        inserted_count = load_products(connection, products)

        # Si aucune erreur ne survient, Psycopg valide
        # automatiquement la transaction à la sortie du bloc.
        # Sinon, il annule les modifications (rollback).

    print(f"Produits réellement insérés : {inserted_count}")


if __name__ == "__main__":
    main()
