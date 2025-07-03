import psycopg2
from psycopg2 import IntegrityError
from entities.user import User

class UserRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email 
                ON users(email);
            """)
            
            self.db_connection.commit()
            
        except Exception:
            self.db_connection.rollback()
            raise  # Let Flask handle the error
        finally:
            cursor.close()
    
    def save_user(self, user):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (email, password_hash) 
                VALUES (%s, %s) RETURNING id;
            """, (user.email, user.password_hash))
            
            user.id = cursor.fetchone()[0]
            self.db_connection.commit()
            return True
        except IntegrityError:
            self.db_connection.rollback()
            return False
        finally:
            cursor.close()
    
    def get_user_by_email(self, email):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("""
                SELECT id, email, password_hash 
                FROM users WHERE email = %s;
            """, (email,))
            
            row = cursor.fetchone()
            
            if row:
                return User.create_with_stored_data(
                    user_id=row[0],
                    email=row[1], 
                    password_hash=row[2]
                )
            return None
        except Exception:
            return None
        finally:
            cursor.close()