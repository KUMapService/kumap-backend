import sys
from mysql.connector import Error
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from app.core.config import ROOT_PW, USER_NAME, USER_PW, DATABASE_NAME  # noqa: E402
from src.init import create_connection  # noqa: E402


def create_database(connection: object, query: str) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("# Database created successfully.")
    except Error as err:
        print(f'Error: "{err}"')

def create_user(connection: object, username: str, password: str) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}';"
        )
        print("# User created successfully.")
    except Error as err:
        print(f'Error: "{err}"')

def grant_privileges(connection: object, username: str, database: str) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"GRANT ALL PRIVILEGES ON {database}.* TO '{username}'@'localhost';"
        )
        connection.commit()
        print("# Privileges granted successfully.")
    except Error as err:
        print(f'Error: "{err}"')


if __name__ == "__main__":
    print("localhost", "root", ROOT_PW)
    connection = create_connection("localhost", "root", ROOT_PW)
    create_database(connection, f"CREATE DATABASE {DATABASE_NAME}")
    create_user(connection, USER_NAME, USER_PW)
    grant_privileges(connection, USER_NAME, DATABASE_NAME)

    if connection:
        connection.close()
        print("# MySQL connection is closed.")
