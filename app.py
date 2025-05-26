from flask import Flask, g, render_template, request, redirect, url_for, flash
from db import PostgresConnector
import secrets

from controllers.auth_controller import AuthController

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Persistent database connection
db = PostgresConnector(
    # Matches the service name in docker-compose.yml
    host="db",
    # Internal port (not the mapped host port)
    port=5432,
    database="safe_companions_db",
    user="postgres",
    password="password",
)

# Authentication controller
auth_controller = AuthController()


def get_db_conn():
    if "db_conn" not in g:
        g.db_conn = db.get_connection()
    return g.db_conn


@app.teardown_appcontext
def close_db_conn(exception):
    conn = g.pop("db_conn", None)
    if conn:
        db.return_connection(conn)


@app.route("/")
@app.route("/home")
def index():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        version = result[0] if result else "Unavailable"
        cursor.close()
    except Exception:
        version = "Unavailable"

    return render_template("index.html", version=version)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if auth_controller.authenticate(email, password):
            # Successful login
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
