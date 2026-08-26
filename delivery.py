from datetime import datetime, timedelta

# ================================================================
#          TARA INNOVATIONS - DELIVERY SCHEDULE SYSTEM
# ================================================================

ARTICLES = {

    # ------------------------------------------------------------
    # COW LINING
    # ------------------------------------------------------------

    "CL-001": {
        "name": "Cow Lining",
        "production_days": 16,

        "processes": [
            ("WB Issue", 16),
            ("Shaving", 15),
            ("Dye House", 14),
            ("Vacuum", 12),
            ("Crusting", 10),
            ("Buffing/Snuffing", 8),
            ("Finishing", 6),
            ("Final Plating", 3)
        ]
    },

    # ------------------------------------------------------------
    # GOAT LINING
    # SAME PROCESS AS COW LINING
    # ------------------------------------------------------------

    "GL-001": {
        "name": "Goat Lining",
        "production_days": 14,

        "processes": [
            ("WB Issue", 16),
            ("Shaving", 15),
            ("Dye House", 14),
            ("Vacuum", 12),
            ("Crusting", 10),
            ("Buffing/Snuffing", 8),
            ("Finishing", 6),
            ("Final Plating", 3)
        ]
    }
}


# ================================================================
# FIND ARTICLE
# ================================================================

def find_article(article_input):

    article_input = article_input.strip().lower()

    for code, article in ARTICLES.items():

        if article_input == code.lower():
            return code, article

        if article_input == article["name"].lower():
            return code, article

    return None, None


# ================================================================
# GET ORDER DATE
# ================================================================

def get_order_date():

    while True:

        date_input = input(
            "Enter Order Date (DD-MM-YYYY): "
        ).strip()

        try:

            return datetime.strptime(
                date_input,
                "%d-%m-%Y"
            ).date()

        except ValueError:

            print()
            print("ERROR: Invalid date.")
            print("Please enter date like: 25-08-2026")
            print()


# ================================================================
# CALCULATE DELIVERY DATE
# ================================================================

def calculate_delivery_date(
    order_date,
    production_days
):

    return order_date + timedelta(
        days=production_days
    )


# ================================================================
# CALCULATE PROCESS DATES
# ================================================================

def calculate_process_dates(
    delivery_date,
    processes
):

    schedule = []

    for process_name, days_before_delivery in processes:

        process_date = (
            delivery_date
            - timedelta(days=days_before_delivery)
        )

        schedule.append(
            (
                process_name,
                days_before_delivery,
                process_date
            )
        )

    return schedule


# ================================================================
# DISPLAY PROCESS SCHEDULE
# ================================================================

def display_process_schedule(schedule):

    print()
    print("=" * 75)
    print("PROCESS SCHEDULE")
    print("=" * 75)

    print()

    print(
        f"{'PROCESS':<25}"
        f"{'DAYS BEFORE DELIVERY':<25}"
        f"{'PROCESS DATE'}"
    )

    print("-" * 75)

    for process_name, days_before, process_date in schedule:

        print(
            f"{process_name:<25}"
            f"{days_before:<25}"
            f"{process_date.strftime('%d-%m-%Y')}"
        )

    print("-" * 75)


# ================================================================
# MAIN PROGRAM
# ================================================================

def main():

    print()
    print("=" * 75)
    print("                    TARA INNOVATIONS")
    print("                 DELIVERY SCHEDULE SYSTEM")
    print("=" * 75)
    print()

    # ------------------------------------------------------------
    # SUPPLIER
    # ------------------------------------------------------------

    supplier_name = input(
        "Enter Supplier Name: "
    ).strip()

    print()

    # ------------------------------------------------------------
    # AVAILABLE ARTICLES
    # ------------------------------------------------------------

    print("AVAILABLE ARTICLES")
    print()

    for code, article in ARTICLES.items():

        print(
            f"  {code}  -  "
            f"{article['name']}  -  "
            f"{article['production_days']} Days"
        )

    print()

    # ------------------------------------------------------------
    # ARTICLE INPUT
    # ------------------------------------------------------------

    article_input = input(
        "Enter Article Code or Article Name: "
    ).strip()

    # ------------------------------------------------------------
    # FIND ARTICLE
    # ------------------------------------------------------------

    article_code, article = find_article(
        article_input
    )

    if article is None:

        print()
        print("=" * 75)
        print("ERROR: ARTICLE NOT FOUND")
        print("=" * 75)
        print()

        return

    # ------------------------------------------------------------
    # SELECTED ARTICLE
    # ------------------------------------------------------------

    print()
    print("SELECTED ARTICLE")
    print("-" * 40)

    print(
        "Article Name    : "
        + article["name"]
    )

    print(
        "Article Code    : "
        + article_code
    )

    print(
        "Production Time : "
        + str(article["production_days"])
        + " Days"
    )

    print()

    # ------------------------------------------------------------
    # ORDER DATE
    # ------------------------------------------------------------

    order_date = get_order_date()

    # ------------------------------------------------------------
    # CALCULATE FINAL DELIVERY DATE
    # ------------------------------------------------------------

    delivery_date = calculate_delivery_date(
        order_date,
        article["production_days"]
    )

    # ------------------------------------------------------------
    # CALCULATE PROCESS SCHEDULE
    # ------------------------------------------------------------

    schedule = calculate_process_dates(
        delivery_date,
        article["processes"]
    )

    # ============================================================
    # FINAL RESULT
    # ============================================================

    print()
    print("=" * 75)
    print("                    DELIVERY RESULT")
    print("=" * 75)

    print()

    print(
        "Supplier Name       : "
        + supplier_name
    )

    print(
        "Article Name        : "
        + article["name"]
    )

    print(
        "Article Code        : "
        + article_code
    )

    print(
        "Order Date          : "
        + order_date.strftime("%d-%m-%Y")
    )

    print(
        "Production Time     : "
        + str(article["production_days"])
        + " Days"
    )

    print()

    print(
        "FINAL DELIVERY DATE : "
        + delivery_date.strftime("%d-%m-%Y")
    )

    # ------------------------------------------------------------
    # PROCESS SCHEDULE
    # ------------------------------------------------------------

    display_process_schedule(
        schedule
    )

    # ------------------------------------------------------------
    # SUCCESS MESSAGE
    # ------------------------------------------------------------

    print()
    print("=" * 75)
    print("     DELIVERY SCHEDULE GENERATED SUCCESSFULLY")
    print("=" * 75)
    print()


# ================================================================
# START PROGRAM
# ================================================================

if __name__ == "__main__":

    main()