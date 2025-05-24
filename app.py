from flask import Flask, g, render_template
from db import PostgresConnector

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True)
