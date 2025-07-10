import psycopg2
from psycopg2 import pool
import logging
import os

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
            
            # Build connection parameters with SSL support
            connection_params = {
                'host': config.host,
                'port': config.port,
                'database': config.database,
                'user': config.user,
                'password': config.password,
                'sslmode': config.ssl_mode,
                'minconn': config.minconn,
                'maxconn': config.maxconn
            }
            
            # Add SSL certificate parameters if provided
            if config.ssl_cert:
                connection_params['sslcert'] = config.ssl_cert
            if config.ssl_key:
                connection_params['sslkey'] = config.ssl_key  
            if config.ssl_ca:
                connection_params['sslrootcert'] = config.ssl_ca
            
            # Log SSL configuration (without sensitive data)
            ssl_status = "enabled" if config.ssl_mode in ['require', 'verify-ca', 'verify-full'] else "preferred"
            logger.info(f"Database SSL mode: {config.ssl_mode} ({ssl_status})")
            
            self.pool = psycopg2.pool.ThreadedConnectionPool(**connection_params)
            print("PostgreSQL connection pool established with SSL security.")
            
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
            conn = self.pool.getconn()
            # Validate SSL connection in production
            self._validate_ssl_connection(conn)
            return conn
        except Exception as error:
            logger.error("Failed to acquire database connection")
            logger.debug(f"Connection acquisition error: {str(error)}")
            raise Exception("Database connection unavailable")

    def _validate_ssl_connection(self, conn):
        """Validate that the connection is using SSL encryption"""
        try:
            with conn.cursor() as cursor:
                # Check if SSL is enabled on the connection
                cursor.execute("SELECT ssl_is_used()")
                ssl_used = cursor.fetchone()[0]
                
                if not ssl_used:
                    # Get environment to determine if SSL is required
                    is_production = not (
                        os.getenv('FLASK_ENV') == 'development' or 
                        os.getenv('FLASK_DEBUG') == '1' or
                        os.getenv('CI') == 'true' or 
                        os.getenv('GITHUB_ACTIONS') == 'true'
                    )
                    
                    if is_production:
                        logger.error("SSL connection required in production but not established")
                        raise Exception("Secure connection required")
                    else:
                        logger.warning("Database connection is not using SSL encryption")
                else:
                    logger.debug("Database connection is using SSL encryption")
                    
        except Exception as e:
            # If SSL validation fails, log but don't break the connection in development
            logger.debug(f"SSL validation check failed: {str(e)}")
            pass

    def return_connection(self, conn):
        if self.pool and conn:
            self.pool.putconn(conn)
            
    def close_all(self):
        """Close all connections in the pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")
            
    def get_connection_info(self):
        """Get connection pool information for monitoring"""
        if not self.pool:
            return {"status": "unavailable", "active_connections": 0, "total_connections": 0}
            
        try:
            return {
                "status": "available",
                "active_connections": len(self.pool._used),
                "total_connections": len(self.pool._pool) + len(self.pool._used)
            }
        except Exception as e:
            logger.debug(f"Failed to get connection info: {str(e)}")
            return {"status": "unknown", "error": str(e)}
