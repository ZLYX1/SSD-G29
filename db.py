import psycopg2
from psycopg2 import pool


class PostgresConnector:

    def __init__(
            self,
            host: str,
            port: int,
            database: str,
            user: str,
            password: str,
            minconn=1,
            maxconn=10,
    ):
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=minconn,
                maxconn=maxconn,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )
            print("PostgreSQL connection pool established.")
        except Exception as error:
            print(f"Failed to create connection pool: {error}")
            self.pool = None

    def get_connection(self):
        if not self.pool:
            raise Exception("Connection pool not initialised")
        return self.pool.getconn()

    def return_connection(self, conn):
        if self.pool and conn:
            self.pool.putconn(conn)

    def close_all(self):
        if self.pool:
            self.pool.closeall()
            print("PostgreSQL connection pool closed.")
