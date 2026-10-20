import random
from decimal import Decimal
from datetime import datetime, timezone


def generate_customers(
    count: int = 100, seed: int = 42, start_id: int = 1001
) -> list[dict]:
    """
    Génère une liste reproductible de clients fictifs.

    Paramètres :
        count : nombre de clients à générer.
        seed : graine utilisée pour reproduire les résultats.

    Retour :
        Liste de dictionnaires représentant les clients.
    """

    # Créer un générateur aléatoire indépendant.
    rng = random.Random(seed)

    # Référentiels simplifiés de notre CRM.
    first_names = ["Alice", "Lucas", "Emma", "Hugo", "Sofia"]
    last_names = ["Martin", "Bernard", "Dubois", "Petit", "Moreau"]
    countries = ["FR", "BE", "CH", "DE", "ES"]

    # Liste destinée à recevoir les clients générés.
    customers = []

    # Générer les identifiants à partir de start_id.
    # La borne supérieure de range() est exclue.
    for customer_id in range(start_id, start_id + count):

        # Sélectionner des valeurs fictives dans nos référentiels.
        first_name = rng.choice(first_names)
        last_name = rng.choice(last_names)
        country_code = rng.choice(countries)

        # Construire une adresse e-mail fictive et unique.
        email = (
            f"{first_name.lower()}.{last_name.lower()}." f"{customer_id}@example.com"
        )

        # Construire l'enregistrement du client.
        customer = {
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "country_code": country_code,
            "created_at": datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc),
        }

        customers.append(customer)

    return customers


def generate_products(
    count: int = 10, seed: int = 42, start_id: int = 2001
) -> list[dict]:
    """
    Génère une liste reproductible de produits fictifs.

    Paramètres :
        count : nombre de produits à générer.
        seed : graine pour reproduire les résultats.
        start_id : premier identifiant produit.

    Retour :
        Liste de dictionnaires représentant les produits.
    """

    # Générateur pseudo-aléatoire indépendant.
    rng = random.Random(seed)

    # Référentiels simplifiés du catalogue.
    categories = ["SPORT", "TEXTILE", "ELECTRONIQUE", "MAISON"]
    currencies = ["EUR", "CHF"]

    # Liste des produits générés.
    products = []

    for product_id in range(start_id, start_id + count):

        # Sélectionner une catégorie et une devise.
        category = rng.choice(categories)
        currency = rng.choice(currencies)

        # Générer un prix positif avec deux décimales.
        price_cents = rng.randint(500, 50000)
        # Convertir les centimes en montant décimal exact.
        # Garantir une précision de deux décimales.
        unit_price = (Decimal(price_cents) / Decimal("100")).quantize(Decimal("0.01"))

        # Construire un produit fictif.
        product = {
            "product_id": product_id,
            "product_name": f"Produit {category} {product_id}",
            "category": category,
            "unit_price": unit_price,
            "currency": currency,
            "is_active": True,
            "created_at": datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc),
        }

        products.append(product)

    return products


def generate_orders(
    count: int = 10, seed: int = 42, start_id: int = 3001
) -> list[dict]:
    """
    Génère des commandes CRM synthétiques.

    Chaque commande devra être rattachée
    à un client existant dans PostgreSQL.
    """

    rng = random.Random(seed)

    # Valeurs autorisées par la contrainte SQL.
    statuses = ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]

    # Liste destinée à recevoir les commandes.
    orders = []

    # Identifiants des 100 clients synthétiques déjà chargés.
    customer_ids = list(range(1001, 1101))

    # Générer les identifiants des commandes.
    for order_id in range(start_id, start_id + count):

        # Sélectionner un client existant.
        customer_id = rng.choice(customer_ids)

        # Choisir un statut autorisé par PostgreSQL.
        status = rng.choice(statuses)

        # Sélectionner une devise autorisée par notre règle métier.
        currencies = ["EUR", "CHF"]
        currency = rng.choice(currencies)

        # Date initiale de la commande en UTC.
        order_date = datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc)

        # À la création, les trois dates sont identiques.
        created_at = order_date
        updated_at = order_date

        # Construire une commande sous forme de dictionnaire.
        order = {
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date,
            "status": status,
            "currency": currency,
            "created_at": created_at,
            "updated_at": updated_at,
        }

        # Ajouter la commande à la liste des commandes.
        orders.append(order)

        # Afficher les informations générées pour contrôle.
        print(
            f"Commande {order_id} -> "
            f"Client {customer_id} -> "
            f"Statut {status} -> "
            f"Devise {currency}"
        )

    return orders


def generate_order_items(
    count: int = 30, seed: int = 42, start_id: int = 4001
) -> list[dict]:
    """
    Génère des lignes de commande CRM synthétiques.

    Chaque ligne devra :
    - référencer une commande existante ;
    - référencer un produit existant ;
    - posséder une quantité strictement positive ;
    - conserver le prix unitaire historique du produit.
    """

    # Générateur pseudo-aléatoire reproductible.
    rng = random.Random(seed)

    # Liste destinée à recevoir les lignes de commande.
    order_items = []

    # Reconstituer le catalogue de référence chargé en base.
    # Même seed et mêmes paramètres = mêmes produits et mêmes prix.
    products = generate_products(count=10, seed=42, start_id=2001)

    # Reconstituer les commandes déjà chargées en base.
    orders = generate_orders(count=10, seed=42, start_id=3001)

    # Indexer les commandes par leur identifiant.
    # Exemple : orders_by_id[3008] retourne la commande 3008.
    orders_by_id = {order["order_id"]: order for order in orders}

    # Identifiants des commandes déjà chargées dans PostgreSQL.
    order_ids = list(range(3001, 3011))

    # Générer les identifiants des lignes de commande.
    for order_item_id in range(start_id, start_id + count):

        # Répartir les lignes entre les 10 commandes existantes.
        # Le modulo permet de revenir à la première commande
        # après avoir parcouru les 10 identifiants.
        index = (order_item_id - start_id) % len(order_ids)
        order_id = order_ids[index]

        # Retrouver la commande et sa devise.
        order = orders_by_id[order_id]
        order_currency = order["currency"]

        # Ne conserver que les produits dans la même devise.
        compatible_products = [
            product for product in products if product["currency"] == order_currency
        ]

        # Choisir un produit compatible de manière reproductible.
        product = rng.choice(compatible_products)

        # Générer une quantité strictement positive.
        quantity = rng.randint(1, 5)

        # Conserver le prix catalogue comme prix historique.
        unit_price = product["unit_price"]

        # Construire une ligne conforme au schéma PostgreSQL.
        order_item = {
            "order_item_id": order_item_id,
            "order_id": order_id,
            "product_id": product["product_id"],
            "quantity": quantity,
            "unit_price": unit_price,
            "created_at": order["created_at"],
            "updated_at": order["updated_at"],
        }

        # Ajouter la ligne à notre liste.
        order_items.append(order_item)

    return order_items


def generate_payments(
    count: int = 10, seed: int = 42, start_id: int = 5001
) -> list[dict]:
    """
    Génère des paiements synthétiques liés aux commandes CRM.

    Règles :
    - chaque paiement référence une commande existante ;
    - le montant correspond au total de ses lignes ;
    - la devise correspond à celle de la commande ;
    - les moyens et statuts respectent les contraintes SQL.
    """

    # Générateur pseudo-aléatoire reproductible.
    rng = random.Random(seed)

    # Reconstituer les commandes et leurs lignes.
    orders = generate_orders(count=10, seed=42, start_id=3001)
    order_items = generate_order_items(count=30, seed=42, start_id=4001)

    # Liste des paiements à construire.
    payments = []

    # Initialiser le montant de chaque commande à zéro.
    # Decimal évite les imprécisions des nombres flottants.
    totals_by_order = {order["order_id"]: Decimal("0.00") for order in orders}

    # Parcourir les lignes de commande pour calculer les montants.
    for item in order_items:

        # Montant de la ligne = quantité × prix unitaire.
        line_total = item["quantity"] * item["unit_price"]

        # Ajouter ce montant au total de la commande correspondante.
        totals_by_order[item["order_id"]] += line_total

        # Moyens et statuts autorisés par PostgreSQL.
    payment_methods = ["CARD", "BANK_TRANSFER", "PAYPAL"]
    payment_statuses = ["PENDING", "PAID", "FAILED", "REFUNDED"]

    # Générer un paiement par commande.
    for index, order in enumerate(orders[:count]):

        # Construire un identifiant unique.
        payment_id = start_id + index

        # Retrouver le montant calculé pour cette commande.
        amount = totals_by_order[order["order_id"]]

        # Choisir un moyen et un statut de manière reproductible.
        payment_method = rng.choice(payment_methods)
        # Règle métier simplifiée pour le jeu de données CRM.
        payment_status_by_order_status = {
            "PENDING": "PENDING",
            "CONFIRMED": "PAID",
            "SHIPPED": "PAID",
            "DELIVERED": "PAID",
            "CANCELLED": "FAILED",
        }

        # Déterminer le statut du paiement selon celui de la commande.
        payment_status = payment_status_by_order_status[order["status"]]

        # Un paiement en attente n'a pas encore de date de paiement.
        payment_date = None if payment_status == "PENDING" else order["order_date"]

        # Construire les neuf champs de la table payments.
        payment = {
            "payment_id": payment_id,
            "order_id": order["order_id"],
            "amount": amount,
            "currency": order["currency"],
            "payment_method": payment_method,
            "payment_status": payment_status,
            "payment_date": payment_date,
            "created_at": order["created_at"],
            "updated_at": order["updated_at"],
        }

        # Ajouter le paiement à notre liste.
        payments.append(payment)

    return payments
