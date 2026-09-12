import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(
    BASE_DIR,
    "database.db"
)


def get_db():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_db()

    cursor = connection.cursor()


    # ==========================================
    # CITIZEN USERS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)


    # ==========================================
    # DEPARTMENT USERS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            department_name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)


    # ==========================================
    # CIVIC REPORTS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            tracking_id TEXT UNIQUE NOT NULL,

            citizen_id INTEGER NOT NULL,

            citizen_name TEXT NOT NULL,

            contact TEXT,

            problem_type TEXT NOT NULL,

            description TEXT NOT NULL,

            location TEXT,

            latitude REAL,

            longitude REAL,

            image_path TEXT,

            priority_score INTEGER DEFAULT 0,

            status TEXT DEFAULT 'Pending',

            assigned_department TEXT,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL,

            FOREIGN KEY (
                citizen_id
            )
            REFERENCES users(id)

        )
    """)


    connection.commit()

    connection.close()


if __name__ == "__main__":

    initialize_database()

    print(
        "NagarDrishti database created successfully."
    )
