import mysql.connector
from mysql.connector import Error


def create_connection(
    host: str,
    user: str,
    password: str,
    database: str | None = None,
) -> mysql.connector.MySQLConnection | None:
    """
    MySQL 데이터베이스 연결 생성 함수
    """
    try:
        conn_args = {"host": host, "user": user, "password": password}
        if database:
            conn_args["database"] = database

        connection = mysql.connector.connect(**conn_args)
        print(f"# ✅ MySQL 연결 성공: {user}@{host}{'/' + database if database else ''}")
        return connection

    except Error as e:
        print(f"# ❌ MySQL 연결 실패: {e}")
        return None
