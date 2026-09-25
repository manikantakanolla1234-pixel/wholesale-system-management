from flask import Flask, render_template, request, redirect, url_for, session
from database import get_connection

app = Flask(__name__)

app.secret_key = "WholesaleManagement2026"


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM admin
            WHERE username=%s
            AND password=%s
        """, (username, password))

        admin = cursor.fetchone()

        cursor.close()
        conn.close()

        if admin:

            session["admin"] = admin["username"]

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template("login.html")


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect(url_for("login"))


# =====================================================
# HOME DASHBOARD
# =====================================================

@app.route("/")
def home():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------------------------------
    # TOTAL PRODUCTS
    # -------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM products
    """)

    total_products = cursor.fetchone()[0]


    # -------------------------------------------------
    # TOTAL CUSTOMERS
    # -------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM customers
    """)

    total_customers = cursor.fetchone()[0]


    # -------------------------------------------------
    # TOTAL BUYERS
    # -------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM buyers
    """)

    total_buyers = cursor.fetchone()[0]


    # -------------------------------------------------
    # TOTAL SALES
    # -------------------------------------------------

    cursor.execute("""
        SELECT IFNULL(SUM(total_amount), 0)
        FROM sales
    """)

    total_sales = cursor.fetchone()[0]


    # -------------------------------------------------
    # PAID AMOUNT
    # -------------------------------------------------

    cursor.execute("""
        SELECT IFNULL(SUM(amount), 0)
        FROM payments
        WHERE payment_status = 'Paid'
    """)

    paid_amount = cursor.fetchone()[0]


    # -------------------------------------------------
    # PENDING PAYMENT AMOUNT
    # -------------------------------------------------

    cursor.execute("""
        SELECT IFNULL(SUM(amount), 0)
        FROM payments
        WHERE payment_status = 'Pending'
    """)

    pending_payments = cursor.fetchone()[0]


    # =================================================
    # MONTHLY SALES DATA
    # =================================================

    cursor.execute("""
        SELECT
            DATE_FORMAT(sale_date, '%Y-%m') AS month,
            IFNULL(SUM(total_amount), 0) AS total
        FROM sales
        GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
        ORDER BY DATE_FORMAT(sale_date, '%Y-%m')
    """)

    sales_chart = cursor.fetchall()


    # =================================================
    # PAYMENT STATUS DATA
    # =================================================

    cursor.execute("""
        SELECT
            payment_status,
            COUNT(*) AS total
        FROM payments
        GROUP BY payment_status
    """)

    payment_chart = cursor.fetchall()


    # =================================================
    # MONTHLY PAYMENT DATA
    # =================================================

    cursor.execute("""
        SELECT
            YEAR(payment_date) AS payment_year,
            MONTH(payment_date) AS payment_month,
            IFNULL(SUM(amount), 0) AS total_amount
        FROM payments
        GROUP BY
            YEAR(payment_date),
            MONTH(payment_date)
        ORDER BY
            YEAR(payment_date),
            MONTH(payment_date)
    """)

    monthly_payments = cursor.fetchall()

    # =================================================
    # EXTRA GRAPH DATA
    # =================================================

    # Sales by product category
    cursor.execute("""
        SELECT
            p.category,
            IFNULL(SUM(s.total_amount), 0) AS total
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.category
        ORDER BY total DESC
    """)
    category_sales = cursor.fetchall()

    # Top selling products by revenue
    cursor.execute("""
        SELECT
            p.product_name,
            IFNULL(SUM(s.quantity), 0) AS quantity,
            IFNULL(SUM(s.total_amount), 0) AS revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY revenue DESC
        LIMIT 10
    """)
    top_products = cursor.fetchall()

    # Monthly profit
    cursor.execute("""
        SELECT
            DATE_FORMAT(s.sale_date, '%Y-%m') AS month,
            IFNULL(SUM((p.selling_price - p.purchase_price) * s.quantity), 0) AS profit
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY DATE_FORMAT(s.sale_date, '%Y-%m')
        ORDER BY DATE_FORMAT(s.sale_date, '%Y-%m')
    """)
    profit_chart = cursor.fetchall()


    cursor.close()
    conn.close()


    # =================================================
    # SEND DATA TO INDEX.HTML
    # =================================================

    return render_template(
        "index.html",

        total_products=total_products,

        total_customers=total_customers,

        total_buyers=total_buyers,

        total_sales=total_sales,

        paid_amount=paid_amount,

        pending_payments=pending_payments,

        sales_chart=sales_chart,

        payment_chart=payment_chart,

        monthly_payments=monthly_payments,

        category_sales=category_sales,

        top_products=top_products,

        profit_chart=profit_chart
    )


# =====================================================
# PRODUCTS
# =====================================================

@app.route("/products_page")
def products_page():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM products
        ORDER BY product_id
    """)

    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "products.html",
        products=products
    )


# -----------------------------------------------------
# ADD PRODUCT
# -----------------------------------------------------

@app.route("/add_product", methods=["GET", "POST"])
def add_product():

    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        product_name = request.form["product_name"]
        category = request.form["category"]
        quantity = request.form["quantity"]
        purchase_price = request.form["purchase_price"]
        selling_price = request.form["selling_price"]
        supplier = request.form["supplier"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO products
            (
                product_name,
                category,
                quantity,
                purchase_price,
                selling_price,
                supplier
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            product_name,
            category,
            quantity,
            purchase_price,
            selling_price,
            supplier
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for("products_page")
        )

    return render_template(
        "add_product.html"
    )


# -----------------------------------------------------
# EDIT PRODUCT
# -----------------------------------------------------

@app.route(
    "/edit_product/<int:id>",
    methods=["GET", "POST"]
)
def edit_product(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        cursor.execute("""
            UPDATE products
            SET
                product_name=%s,
                category=%s,
                quantity=%s,
                purchase_price=%s,
                selling_price=%s,
                supplier=%s
            WHERE product_id=%s
        """, (
            request.form["product_name"],
            request.form["category"],
            request.form["quantity"],
            request.form["purchase_price"],
            request.form["selling_price"],
            request.form["supplier"],
            id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for("products_page")
        )

    cursor.execute("""
        SELECT *
        FROM products
        WHERE product_id=%s
    """, (id,))

    product = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_product.html",
        product=product
    )


# -----------------------------------------------------
# DELETE PRODUCT
# -----------------------------------------------------

@app.route("/delete_product/<int:id>")
def delete_product(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM products
        WHERE product_id=%s
    """, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("products_page")
    )


# =====================================================
# CUSTOMERS
# =====================================================

@app.route("/customers_page")
def customers_page():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY customer_id
    """)

    customers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "customers.html",
        customers=customers
    )


# -----------------------------------------------------
# ADD CUSTOMER
# -----------------------------------------------------

@app.route("/add_customer", methods=["GET", "POST"])
def add_customer():

    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        city = request.form["city"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO customers
            (
                customer_name,
                phone,
                city
            )
            VALUES (%s, %s, %s)
        """, (
            customer_name,
            phone,
            city
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for("customers_page")
        )

    return render_template(
        "add_customer.html"
    )


# -----------------------------------------------------
# EDIT CUSTOMER
# -----------------------------------------------------

@app.route(
    "/edit_customer/<int:id>",
    methods=["GET", "POST"]
)
def edit_customer(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        city = request.form["city"]

        cursor.execute("""
            UPDATE customers
            SET
                customer_name=%s,
                phone=%s,
                city=%s
            WHERE customer_id=%s
        """, (
            customer_name,
            phone,
            city,
            id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for("customers_page")
        )

    cursor.execute("""
        SELECT *
        FROM customers
        WHERE customer_id=%s
    """, (id,))

    customer = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_customer.html",
        customer=customer
    )


# -----------------------------------------------------
# DELETE CUSTOMER
# -----------------------------------------------------

@app.route("/delete_customer/<int:id>")
def delete_customer(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM customers
        WHERE customer_id=%s
    """, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("customers_page")
    )


# =====================================================
# BUYERS
# =====================================================

@app.route("/buyers_page")
def buyers_page():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM buyers
        ORDER BY buyer_id
    """)

    buyers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "buyers.html",
        buyers=buyers
    )


# -----------------------------------------------------
# ADD BUYER
# -----------------------------------------------------

@app.route("/add_buyer", methods=["GET", "POST"])
def add_buyer():

    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        buyer_name = request.form["buyer_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO buyers
            (
                buyer_name,
                phone,
                email,
                address
            )
            VALUES (%s, %s, %s, %s)
        """, (
            buyer_name,
            phone,
            email,
            address
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for("buyers_page")
        )

    return render_template(
        "add_buyer.html"
    )


# -----------------------------------------------------
# EDIT BUYER
# -----------------------------------------------------

@app.route(
    "/edit_buyer/<int:id>",
    methods=["GET", "POST"]
)
def edit_buyer(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        cursor.execute("""
            UPDATE buyers
            SET
                buyer_name=%s,
                phone=%s,
                email=%s,
                address=%s
            WHERE buyer_id=%s
        """, (
            request.form["buyer_name"],
            request.form["phone"],
            request.form["email"],
            request.form["address"],
            id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for("buyers_page")
        )

    cursor.execute("""
        SELECT *
        FROM buyers
        WHERE buyer_id=%s
    """, (id,))

    buyer = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_buyer.html",
        buyer=buyer
    )


# -----------------------------------------------------
# DELETE BUYER
# -----------------------------------------------------

@app.route("/delete_buyer/<int:id>")
def delete_buyer(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM buyers
        WHERE buyer_id=%s
    """, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("buyers_page")
    )


# =====================================================
# SALES
# =====================================================

@app.route("/sales_page")
def sales_page():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # =================================================
    # SALES TABLE DATA
    # =================================================

    cursor.execute("""
        SELECT
            s.sale_id,
            c.customer_name,
            p.product_name,
            s.quantity,
            s.sale_date,
            s.total_amount
        FROM sales s

        JOIN customers c
            ON s.customer_id = c.customer_id

        JOIN products p
            ON s.product_id = p.product_id

        ORDER BY s.sale_id
    """)

    sales = cursor.fetchall()


    # =================================================
    # MONTHLY SALES GRAPH DATA
    # =================================================

    cursor.execute("""
        SELECT
            DATE_FORMAT(sale_date, '%Y-%m') AS month,
            IFNULL(SUM(total_amount), 0) AS total
        FROM sales
        GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
        ORDER BY DATE_FORMAT(sale_date, '%Y-%m')
    """)

    sales_chart = cursor.fetchall()

    # Daily sales trend
    cursor.execute("""
        SELECT
            DATE(sale_date) AS sale_day,
            IFNULL(SUM(total_amount), 0) AS total
        FROM sales
        GROUP BY DATE(sale_date)
        ORDER BY DATE(sale_date)
    """)
    daily_sales_chart = cursor.fetchall()

    # Sales by category
    cursor.execute("""
        SELECT
            p.category,
            IFNULL(SUM(s.total_amount), 0) AS total
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.category
        ORDER BY total DESC
    """)
    sales_category_chart = cursor.fetchall()

    # Top products by quantity
    cursor.execute("""
        SELECT
            p.product_name,
            IFNULL(SUM(s.quantity), 0) AS quantity
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY quantity DESC
        LIMIT 10
    """)
    sales_product_chart = cursor.fetchall()


    # =================================================
    # CLOSE DATABASE
    # =================================================

    cursor.close()
    conn.close()


    # =================================================
    # SEND DATA TO SALES.HTML
    # =================================================

    return render_template(
        "sales.html",
        sales=sales,
        sales_chart=sales_chart,
        daily_sales_chart=daily_sales_chart,
        sales_category_chart=sales_category_chart,
        sales_product_chart=sales_product_chart
    )


# -----------------------------------------------------
# ADD SALE
# -----------------------------------------------------

@app.route("/add_sale", methods=["GET", "POST"])
def add_sale():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        customer_id = request.form["customer_id"]
        product_id = request.form["product_id"]
        quantity = int(request.form["quantity"])
        sale_date = request.form["sale_date"]

        cursor.execute("""
            SELECT selling_price
            FROM products
            WHERE product_id=%s
        """, (product_id,))

        product = cursor.fetchone()

        if not product:

            cursor.close()
            conn.close()

            return "Product not found"

        price = product["selling_price"]

        total_amount = quantity * price

        cursor.execute("""
            INSERT INTO sales
            (
                customer_id,
                product_id,
                quantity,
                sale_date,
                total_amount
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            customer_id,
            product_id,
            quantity,
            sale_date,
            total_amount
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for("sales_page")
        )

    cursor.execute("""
        SELECT
            customer_id,
            customer_name
        FROM customers
        ORDER BY customer_name
    """)

    customers = cursor.fetchall()

    cursor.execute("""
        SELECT
            product_id,
            product_name
        FROM products
        ORDER BY product_name
    """)

    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "add_sale.html",
        customers=customers,
        products=products
    )


# -----------------------------------------------------
# EDIT SALE
# -----------------------------------------------------

@app.route(
    "/edit_sale/<int:id>",
    methods=["GET", "POST"]
)
def edit_sale(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        customer_id = request.form["customer_id"]
        product_id = request.form["product_id"]
        quantity = int(request.form["quantity"])
        sale_date = request.form["sale_date"]

        cursor.execute("""
            SELECT selling_price
            FROM products
            WHERE product_id=%s
        """, (product_id,))

        product = cursor.fetchone()

        if not product:

            cursor.close()
            conn.close()

            return "Product not found"

        price = product["selling_price"]

        total_amount = quantity * price

        cursor.execute("""
            UPDATE sales
            SET
                customer_id=%s,
                product_id=%s,
                quantity=%s,
                sale_date=%s,
                total_amount=%s
            WHERE sale_id=%s
        """, (
            customer_id,
            product_id,
            quantity,
            sale_date,
            total_amount,
            id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for("sales_page")
        )

    cursor.execute("""
        SELECT *
        FROM sales
        WHERE sale_id=%s
    """, (id,))

    sale = cursor.fetchone()

    cursor.execute("""
        SELECT
            customer_id,
            customer_name
        FROM customers
    """)

    customers = cursor.fetchall()

    cursor.execute("""
        SELECT
            product_id,
            product_name
        FROM products
    """)

    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "edit_sale.html",
        sale=sale,
        customers=customers,
        products=products
    )


# -----------------------------------------------------
# DELETE SALE
# -----------------------------------------------------

@app.route("/delete_sale/<int:id>")
def delete_sale(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM sales
        WHERE sale_id=%s
    """, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("sales_page")
    )


# =====================================================
# PAYMENTS
# =====================================================

@app.route("/payments_page")
def payments_page():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.payment_id,
            c.customer_name,
            p.amount,
            p.payment_status,
            p.payment_date
        FROM payments p

        JOIN customers c
            ON p.customer_id = c.customer_id

        ORDER BY p.payment_id
    """)

    payments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "payments.html",
        payments=payments
    )


# -----------------------------------------------------
# ADD PAYMENT
# -----------------------------------------------------

@app.route("/add_payment", methods=["GET", "POST"])
def add_payment():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        customer_id = request.form["customer_id"]
        amount = request.form["amount"]
        payment_status = request.form["payment_status"]
        payment_date = request.form["payment_date"]

        cursor.execute("""
            INSERT INTO payments
            (
                customer_id,
                amount,
                payment_status,
                payment_date
            )
            VALUES (%s, %s, %s, %s)
        """, (
            customer_id,
            amount,
            payment_status,
            payment_date
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for("payments_page")
        )

    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY customer_name
    """)

    customers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "add_payment.html",
        customers=customers
    )


# -----------------------------------------------------
# EDIT PAYMENT
# -----------------------------------------------------

@app.route(
    "/edit_payment/<int:id>",
    methods=["GET", "POST"]
)
def edit_payment(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        customer_id = request.form["customer_id"]
        amount = request.form["amount"]
        payment_status = request.form["payment_status"]
        payment_date = request.form["payment_date"]

        cursor.execute("""
            UPDATE payments
            SET
                customer_id=%s,
                amount=%s,
                payment_status=%s,
                payment_date=%s
            WHERE payment_id=%s
        """, (
            customer_id,
            amount,
            payment_status,
            payment_date,
            id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for("payments_page")
        )

    cursor.execute("""
        SELECT *
        FROM payments
        WHERE payment_id=%s
    """, (id,))

    payment = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY customer_name
    """)

    customers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "edit_payment.html",
        payment=payment,
        customers=customers
    )


# -----------------------------------------------------
# DELETE PAYMENT
# -----------------------------------------------------

@app.route("/delete_payment/<int:id>")
def delete_payment(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM payments
        WHERE payment_id=%s
    """, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("payments_page")
    )


# =====================================================
# MONTHLY PAYMENT REPORT
# =====================================================

@app.route("/monthly_payments")
def monthly_payments():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            YEAR(payment_date) AS payment_year,
            MONTH(payment_date) AS payment_month,
            IFNULL(SUM(amount), 0) AS total_amount,
            COUNT(payment_id) AS payment_count
        FROM payments
        GROUP BY
            YEAR(payment_date),
            MONTH(payment_date)
        ORDER BY
            YEAR(payment_date) DESC,
            MONTH(payment_date) DESC
    """)

    payments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "monthly_payments.html",
        payments=payments
    )


# =====================================================
# PROFIT REPORT
# =====================================================

@app.route("/profit_page")
def profit_page():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            MONTH(s.sale_date) AS month,
            SUM(
                (p.selling_price - p.purchase_price)
                * s.quantity
            ) AS profit
        FROM sales s

        JOIN products p
            ON s.product_id = p.product_id

        GROUP BY MONTH(s.sale_date)

        ORDER BY MONTH(s.sale_date)
    """)

    profit = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "profit.html",
        profit=profit
    )


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )