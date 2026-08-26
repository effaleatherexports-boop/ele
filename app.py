from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import sqlite3
import os


# ================================================================
# FLASK APPLICATION
# ================================================================

app = Flask(
    __name__,
    template_folder="templates"
)

app.secret_key = "ELE_DELIVERY_SECRET_KEY"

DATABASE = "delivery.db"


# ================================================================
# ADMIN LOGIN DETAILS
# ================================================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ================================================================
# DATABASE CONNECTION
# ================================================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# ================================================================
# INITIALIZE DATABASE
# ================================================================

def initialize_database():

    connection = get_db_connection()

    cursor = connection.cursor()


    # ============================================================
    # ARTICLES TABLE
    # ============================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            code TEXT UNIQUE NOT NULL,

            name TEXT NOT NULL,

            production_days INTEGER NOT NULL

        )
    """)


    # ============================================================
    # PROCESSES TABLE
    # ============================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            article_id INTEGER NOT NULL,

            process_name TEXT NOT NULL,

            days_before_delivery INTEGER NOT NULL,

            FOREIGN KEY(article_id)
            REFERENCES articles(id)

        )
    """)


    # ============================================================
    # ORDERS TABLE
    # ============================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            supplier TEXT NOT NULL,

            article_code TEXT NOT NULL,

            article_name TEXT NOT NULL,

            order_date TEXT NOT NULL,

            production_days INTEGER NOT NULL,

            delivery_date TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)


    # ============================================================
    # DEFAULT COW ARTICLE
    # ============================================================

    cursor.execute("""
        INSERT OR IGNORE INTO articles
        (
            code,
            name,
            production_days
        )

        VALUES (?, ?, ?)
    """, (
        "CL-001",
        "Cow Lining",
        16
    ))


    # ============================================================
    # DEFAULT GOAT ARTICLE
    # ============================================================

    cursor.execute("""
        INSERT OR IGNORE INTO articles
        (
            code,
            name,
            production_days
        )

        VALUES (?, ?, ?)
    """, (
        "GL-001",
        "Goat Lining",
        14
    ))


    connection.commit()


    # ============================================================
    # GET COW ARTICLE
    # ============================================================

    cow = cursor.execute("""
        SELECT id
        FROM articles
        WHERE code = ?
    """, (
        "CL-001",
    )).fetchone()


    # ============================================================
    # GET GOAT ARTICLE
    # ============================================================

    goat = cursor.execute("""
        SELECT id
        FROM articles
        WHERE code = ?
    """, (
        "GL-001",
    )).fetchone()


    # ============================================================
    # DEFAULT PROCESS SCHEDULE
    # ============================================================

    default_processes = [

        ("WB Issue", 16),

        ("Shaving", 15),

        ("Dye House", 14),

        ("Vacuum", 12),

        ("Crusting", 10),

        ("Buffing/Snuffing", 8),

        ("Finishing", 6),

        ("Final Plating", 3)

    ]


    # ============================================================
    # ADD DEFAULT PROCESSES TO COW AND GOAT
    # ============================================================

    for article in [cow, goat]:

        if article:

            for process_name, days in default_processes:

                existing_process = cursor.execute("""
                    SELECT id
                    FROM processes

                    WHERE article_id = ?

                    AND process_name = ?

                """, (
                    article["id"],
                    process_name
                )).fetchone()


                if existing_process is None:

                    cursor.execute("""
                        INSERT INTO processes
                        (
                            article_id,
                            process_name,
                            days_before_delivery
                        )

                        VALUES (?, ?, ?)

                    """, (
                        article["id"],
                        process_name,
                        days
                    ))


    connection.commit()

    connection.close()


# ================================================================
# ADMIN LOGIN
# ================================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    error = None


    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()


        password = request.form.get(
            "password",
            ""
        ).strip()


        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin_dashboard")
            )


        else:

            error = "Invalid username or password."


    return render_template(
        "admin_login.html",
        error=error
    )


# ================================================================
# ADMIN LOGOUT
# ================================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("admin_login")
    )


# ================================================================
# ADMIN DASHBOARD
# ================================================================

@app.route("/admin")
def admin_dashboard():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    connection = get_db_connection()


    articles = connection.execute("""
        SELECT *
        FROM articles
        ORDER BY name
    """).fetchall()


    connection.close()


    return render_template(
        "admin.html",
        articles=articles
    )


# ================================================================
# ADD NEW ARTICLE
# ================================================================

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    if request.method == "POST":

        code = request.form.get(
            "code",
            ""
        ).strip()


        name = request.form.get(
            "name",
            ""
        ).strip()


        production_days = int(
            request.form.get(
                "production_days",
                0
            )
        )


        process_names = [

            "WB Issue",

            "Shaving",

            "Dye House",

            "Vacuum",

            "Crusting",

            "Buffing/Snuffing",

            "Finishing",

            "Final Plating"

        ]


        connection = get_db_connection()


        try:

            cursor = connection.cursor()


            # ----------------------------------------------------
            # ADD ARTICLE
            # ----------------------------------------------------

            cursor.execute("""
                INSERT INTO articles
                (
                    code,
                    name,
                    production_days
                )

                VALUES (?, ?, ?)

            """, (
                code,
                name,
                production_days
            ))


            article_id = cursor.lastrowid


            # ----------------------------------------------------
            # ADD PROCESSES
            # ----------------------------------------------------

            for process_name in process_names:

                days = int(
                    request.form.get(
                        process_name,
                        0
                    )
                )


                cursor.execute("""
                    INSERT INTO processes
                    (
                        article_id,
                        process_name,
                        days_before_delivery
                    )

                    VALUES (?, ?, ?)

                """, (
                    article_id,
                    process_name,
                    days
                ))


            connection.commit()


        except sqlite3.IntegrityError:

            connection.close()

            return "Article code already exists."


        connection.close()


        return redirect(
            url_for("admin_dashboard")
        )


    return render_template(
        "admin_add.html"
    )


# ================================================================
# EDIT ARTICLE
# ================================================================

@app.route(
    "/admin/edit/<int:article_id>",
    methods=["GET", "POST"]
)
def admin_edit(article_id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    connection = get_db_connection()


    article = connection.execute("""
        SELECT *
        FROM articles
        WHERE id = ?
    """, (
        article_id,
    )).fetchone()


    if article is None:

        connection.close()

        return "Article not found."


    processes = connection.execute("""
        SELECT *
        FROM processes

        WHERE article_id = ?

        ORDER BY id

    """, (
        article_id,
    )).fetchall()


    connection.close()


    # ============================================================
    # UPDATE ARTICLE
    # ============================================================

    if request.method == "POST":

        code = request.form.get(
            "code",
            ""
        ).strip()


        name = request.form.get(
            "name",
            ""
        ).strip()


        production_days = int(
            request.form.get(
                "production_days",
                0
            )
        )


        process_names = [

            "WB Issue",

            "Shaving",

            "Dye House",

            "Vacuum",

            "Crusting",

            "Buffing/Snuffing",

            "Finishing",

            "Final Plating"

        ]


        connection = get_db_connection()


        try:

            connection.execute("""
                UPDATE articles

                SET
                    code = ?,
                    name = ?,
                    production_days = ?

                WHERE id = ?

            """, (
                code,
                name,
                production_days,
                article_id
            ))


            for process_name in process_names:

                days = int(
                    request.form.get(
                        process_name,
                        0
                    )
                )


                connection.execute("""
                    UPDATE processes

                    SET
                        days_before_delivery = ?

                    WHERE article_id = ?

                    AND process_name = ?

                """, (
                    days,
                    article_id,
                    process_name
                ))


            connection.commit()


        except sqlite3.IntegrityError:

            connection.close()

            return "That article code already exists."


        connection.close()


        return redirect(
            url_for("admin_dashboard")
        )


    return render_template(
        "admin_edit.html",
        article=article,
        processes=processes
    )


# ================================================================
# DELETE ARTICLE
# ================================================================

@app.route(
    "/admin/delete/<int:article_id>",
    methods=["POST"]
)
def admin_delete(article_id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    connection = get_db_connection()


    # Delete processes first

    connection.execute("""
        DELETE FROM processes

        WHERE article_id = ?

    """, (
        article_id,
    ))


    # Delete article

    connection.execute("""
        DELETE FROM articles

        WHERE id = ?

    """, (
        article_id,
    ))


    connection.commit()

    connection.close()


    return redirect(
        url_for("admin_dashboard")
    )


# ================================================================
# EMPLOYEE DELIVERY SCHEDULE
# ================================================================

@app.route("/", methods=["GET", "POST"])
def home():

    result = None


    # ============================================================
    # GET ARTICLES
    # ============================================================

    connection = get_db_connection()


    articles = connection.execute("""
        SELECT *
        FROM articles
        ORDER BY name
    """).fetchall()


    connection.close()


    # ============================================================
    # CALCULATE DELIVERY
    # ============================================================

    if request.method == "POST":

        supplier = request.form.get(
            "supplier",
            ""
        ).strip()


        article_code = request.form.get(
            "article",
            ""
        ).strip()


        order_date_text = request.form.get(
            "order_date",
            ""
        ).strip()


        if not supplier:

            return "Please enter supplier name."


        if not article_code:

            return "Please select an article."


        if not order_date_text:

            return "Please enter order date."


        # --------------------------------------------------------
        # FIND ARTICLE
        # --------------------------------------------------------

        connection = get_db_connection()


        article = connection.execute("""
            SELECT *
            FROM articles

            WHERE code = ?

        """, (
            article_code,
        )).fetchone()


        if article is None:

            connection.close()

            return "Article not found."


        # --------------------------------------------------------
        # GET PROCESSES
        # --------------------------------------------------------

        processes = connection.execute("""
            SELECT *

            FROM processes

            WHERE article_id = ?

            ORDER BY id

        """, (
            article["id"],
        )).fetchall()


        connection.close()


        # --------------------------------------------------------
        # CONVERT ORDER DATE
        # --------------------------------------------------------

        try:

            order_date = datetime.strptime(
                order_date_text,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            return "Invalid date."


        # --------------------------------------------------------
        # GET PRODUCTION DAYS
        # --------------------------------------------------------

        production_days = article[
            "production_days"
        ]


        # --------------------------------------------------------
        # CALCULATE FINAL DELIVERY DATE
        # --------------------------------------------------------

        delivery_date = (

            order_date

            +

            timedelta(
                days=production_days
            )

        )


        # ========================================================
        # PROCESS RESULTS
        # ========================================================

        process_results = []


        for process in processes:

            process_date = (

                delivery_date

                -

                timedelta(
                    days=process[
                        "days_before_delivery"
                    ]
                )

            )


            process_results.append({

                "name":
                process["process_name"],

                "days_before":
                process[
                    "days_before_delivery"
                ],

                "date":
                process_date.strftime(
                    "%d-%m-%Y"
                )

            })


        # ========================================================
        # SAVE ORDER TO SQLITE
        # ========================================================

        connection = get_db_connection()


        connection.execute("""
            INSERT INTO orders
            (
                supplier,
                article_code,
                article_name,
                order_date,
                production_days,
                delivery_date,
                created_at
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)

        """, (

            supplier,

            article["code"],

            article["name"],

            order_date.strftime(
                "%Y-%m-%d"
            ),

            production_days,

            delivery_date.strftime(
                "%Y-%m-%d"
            ),

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        ))


        connection.commit()

        connection.close()


        # ========================================================
        # RESULT
        # ========================================================

        result = {

            "supplier":
            supplier,

            "article_name":
            article["name"],

            "article_code":
            article["code"],

            "order_date":
            order_date.strftime(
                "%d-%m-%Y"
            ),

            "production_days":
            production_days,

            "delivery_date":
            delivery_date.strftime(
                "%d-%m-%Y"
            ),

            "processes":
            process_results

        }


    return render_template(

        "index.html",

        result=result,

        articles=articles

    )


# ================================================================
# ORDER HISTORY
# ================================================================

@app.route("/admin/orders")
def admin_orders():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    connection = get_db_connection()


    orders = connection.execute("""
        SELECT *
        FROM orders

        ORDER BY id DESC

    """).fetchall()


    connection.close()


    return render_template(

        "orders.html",

        orders=orders

    )


# ================================================================
# START APPLICATION
# ================================================================

if __name__ == "__main__":

    initialize_database()


    print()

    print("=" * 60)

    print("E-L-E DELIVERY SCHEDULE SYSTEM")

    print("=" * 60)

    print()


    print(
        "Database:",
        os.path.abspath(DATABASE)
    )


    print()


    print(
        "Employee Website:"
    )


    print(
        "http://127.0.0.1:5000"
    )


    print()


    print(
        "Admin:"
    )


    print(
        "http://127.0.0.1:5000/admin"
    )


    print()


    print(
        "Order History:"
    )


    print(
        "http://127.0.0.1:5000/admin/orders"
    )


    print()


    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )