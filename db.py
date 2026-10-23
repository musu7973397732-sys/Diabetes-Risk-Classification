"""
Database Access Layer for Diabetes Risk Classification System.
Supports MySQL as the primary database with an automatic SQLite fallback for zero-configuration testing.
"""

import os
import sqlite3
from config import Config

# Attempt MySQL Connector Import
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diabetes_db.sqlite3")

def get_db_connection():
    """
    Establishes and returns an active database connection.
    Attempts MySQL first; falls back to SQLite if MySQL is offline.
    Returns: (connection, db_type: str)
    """
    if MYSQL_AVAILABLE:
        try:
            conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                port=Config.MYSQL_PORT
            )
            if conn.is_connected():
                return conn, "mysql"
        except Exception as e:
            print(f"[Database Warning] MySQL connection failed ({e}). Utilizing SQLite fallback for portability.")

    # Fallback to local SQLite database
    try:
        conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"
    except Exception as e:
        print(f"[Database Error] Could not establish database connection: {e}")
        return None, None

def init_db():
    """
    Ensures required tables ('users' and 'prediction_history') exist in the database.
    """
    conn, db_type = get_db_connection()
    if conn is None:
        print("[Database Error] Database initialization aborted: No active connection.")
        return False

    cursor = conn.cursor()
    try:
        if db_type == "mysql":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    pregnancies INT NOT NULL,
                    glucose FLOAT NOT NULL,
                    blood_pressure FLOAT NOT NULL,
                    skin_thickness FLOAT NOT NULL,
                    insulin FLOAT NOT NULL,
                    bmi FLOAT NOT NULL,
                    diabetes_pedigree_function FLOAT NOT NULL,
                    age INT NOT NULL,
                    predicted_outcome TINYINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_prediction_user
                        FOREIGN KEY (user_id) REFERENCES users(id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            conn.commit()

        elif db_type == "sqlite":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    pregnancies INTEGER NOT NULL,
                    glucose REAL NOT NULL,
                    blood_pressure REAL NOT NULL,
                    skin_thickness REAL NOT NULL,
                    insulin REAL NOT NULL,
                    bmi REAL NOT NULL,
                    diabetes_pedigree_function REAL NOT NULL,
                    age INTEGER NOT NULL,
                    predicted_outcome INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)
            conn.commit()

        print(f"[Database] Schema initialized successfully using {db_type.upper()}.")
        return True

    except Exception as e:
        print(f"[Database Error] Schema initialization failed: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def find_user_by_email(email):
    """
    Retrieves a user dictionary by their email address using parameterized SQL.
    """
    conn, db_type = get_db_connection()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True) if db_type == "mysql" else conn.cursor()
    try:
        query = "SELECT * FROM users WHERE email = %s" if db_type == "mysql" else "SELECT * FROM users WHERE email = ?"
        cursor.execute(query, (email.lower().strip(),))
        row = cursor.fetchone()
        if row and db_type == "sqlite":
            return dict(row)
        return row
    except Exception as e:
        print(f"[Database Error] find_user_by_email failed: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def find_user_by_id(user_id):
    """
    Retrieves a user dictionary by their user_id.
    """
    conn, db_type = get_db_connection()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True) if db_type == "mysql" else conn.cursor()
    try:
        query = "SELECT * FROM users WHERE id = %s" if db_type == "mysql" else "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        if row and db_type == "sqlite":
            return dict(row)
        return row
    except Exception as e:
        print(f"[Database Error] find_user_by_id failed: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def insert_user(name, email, hashed_password):
    """
    Inserts a newly registered user into the database.
    Returns: (success: bool, error_code: str or None)
    """
    conn, db_type = get_db_connection()
    if conn is None:
        return False, "DB_CONNECTION_FAILED"

    cursor = conn.cursor()
    try:
        if db_type == "mysql":
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name.strip(), email.lower().strip(), hashed_password)
            )
        else:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name.strip(), email.lower().strip(), hashed_password)
            )
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        # Handle unique constraint violation on email
        if db_type == "mysql" and getattr(e, "errno", None) == 1062:
            return False, "DUPLICATE_EMAIL"
        elif db_type == "sqlite" and "UNIQUE constraint failed" in str(e):
            return False, "DUPLICATE_EMAIL"
        print(f"[Database Error] insert_user failed: {e}")
        return False, "INSERT_FAILED"
    finally:
        cursor.close()
        conn.close()

def insert_prediction(user_id, pregnancies, glucose, blood_pressure, skin_thickness,
                      insulin, bmi, dpf, age, predicted_outcome):
    """
    Stores an ML prediction result in the database linked to the user's ID.
    Returns: bool
    """
    conn, db_type = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    try:
        if db_type == "mysql":
            query = """
                INSERT INTO prediction_history
                (user_id, pregnancies, glucose, blood_pressure, skin_thickness,
                 insulin, bmi, diabetes_pedigree_function, age, predicted_outcome)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        else:
            query = """
                INSERT INTO prediction_history
                (user_id, pregnancies, glucose, blood_pressure, skin_thickness,
                 insulin, bmi, diabetes_pedigree_function, age, predicted_outcome)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        cursor.execute(query, (
            user_id, pregnancies, glucose, blood_pressure, skin_thickness,
            insulin, bmi, dpf, age, int(predicted_outcome)
        ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[Database Error] insert_prediction failed: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_predictions(user_id, limit=50):
    """
    Retrieves the prediction history specifically for the logged-in user, newest first.
    Never exposes another user's records.
    """
    conn, db_type = get_db_connection()
    if conn is None:
        return []

    cursor = conn.cursor(dictionary=True) if db_type == "mysql" else conn.cursor()
    try:
        if db_type == "mysql":
            cursor.execute(
                "SELECT * FROM prediction_history WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
                (user_id, limit)
            )
            return cursor.fetchall()
        else:
            cursor.execute(
                "SELECT * FROM prediction_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            )
            return [dict(r) for r in cursor.fetchall()]
    except Exception as e:
        print(f"[Database Error] get_user_predictions failed: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_user_prediction_count(user_id):
    """
    Returns the total count of predictions performed by the user.
    """
    conn, db_type = get_db_connection()
    if conn is None:
        return 0

    cursor = conn.cursor()
    try:
        query = "SELECT COUNT(*) FROM prediction_history WHERE user_id = %s" if db_type == "mysql" else "SELECT COUNT(*) FROM prediction_history WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"[Database Error] get_user_prediction_count failed: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()
