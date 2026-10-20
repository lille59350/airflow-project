"""
Chargement des paiements synthétiques dans PostgreSQL.

Projet : NovaRetail CRM Data Platform
TP 3.5 : Payments

Objectif :
- Générer les paiements CRM.
- Charger les données dans public.payments.
- Garantir l'atomicité de la transaction.
- Éviter les doublons lors des réexécutions.
"""

from scripts.data_generation.generate_crm_data import generate_payments
from scripts.data_generation.load_customers import connect_to_postgresql


def load_payments() -> None:
    """
    Génère et charge les paiements dans PostgreSQL.

    La transaction est validée uniquement si toutes les
    opérations se déroulent correctement.
    """

    # 1. Générer les 10 paiements reproductibles.
    payments = generate_payments(
        count=10,
        seed=42,
        start_id=5001,
    )

    print("\n=== CHARGEMENT PAYMENTS ===")
    print("Lignes générées :", len(payments))

    # 2. Préparer la requête SQL paramétrée.
    insert_sql = """
        INSERT INTO public.payments (
            payment_id,
            order_id,
            amount,
            currency,
            payment_method,
            payment_status,
            payment_date,
            created_at,
            updated_at
        )
        VALUES (
            %(payment_id)s,
            %(order_id)s,
            %(amount)s,
            %(currency)s,
            %(payment_method)s,
            %(payment_status)s,
            %(payment_date)s,
            %(created_at)s,
            %(updated_at)s
        )
        ON CONFLICT (payment_id) DO NOTHING;
    """

    # 3. Ouvrir la connexion à PostgreSQL.
    with connect_to_postgresql() as connection:

        # 4. Créer un curseur SQL.
        with connection.cursor() as cursor:

            inserted_count = 0

            # 5. Insérer chaque paiement.
            for payment in payments:

                cursor.execute(insert_sql, payment)

                # rowcount vaut 1 si une ligne est insérée,
                # et 0 si le paiement existe déjà.
                inserted_count += cursor.rowcount

        # La sortie normale du bloc connection
        # valide automatiquement la transaction.

    print("Lignes insérées :", inserted_count)


if __name__ == "__main__":
    load_payments()
