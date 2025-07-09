import psycopg2
from psycopg2 import pool
import logging

from config.db_config import DBConfig

# Configure logging for database operations
logger = logging.getLogger(__name__)


class PostgresConnector:

    def __init__(self, config: DBConfig):
        try:
            # print("\n")
            # print("config.port is:")
            # print(config.port)
            # print("\n")
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
            # Log detailed error for administrators, but don't expose system details to users
            logger.error(f"Database connection pool initialization failed. Check database configuration.")
            logger.debug(f"Database error details: {str(error)}")  # Debug level for detailed error
            print("Database connection unavailable. Please try again later.")
            self.pool = None

    def get_connection(self):
        if not self.pool:
            logger.warning("Attempted to get connection from uninitialized pool")
            raise Exception("Database service temporarily unavailable")
        try:
            return self.pool.getconn()
        except Exception as error:
            logger.error("Failed to acquire database connection")
            logger.debug(f"Connection acquisition error: {str(error)}")
            raise Exception("Database connection unavailable")

    def return_connection(self, conn):
        if self.pool and conn:
            self.pool.putconn(conn)

    def close_all(self):
        if self.pool:
            self.pool.closeall()
            print("PostgreSQL connection pool closed.")
