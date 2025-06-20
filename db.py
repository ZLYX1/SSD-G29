import psycopg2
from psycopg2 import pool

from config.db_config import DBConfig


class PostgresConnector:

    def __init__(self, config: DBConfig):
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=config.minconn,
                maxconn=config.maxconn,
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.user,
                password=config.password,
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
