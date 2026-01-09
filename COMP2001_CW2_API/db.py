# db.py
import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    """
    Returns a new SQL Server connection using env vars from .env
    """
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")

    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=Yes;"
        "TrustServerCertificate=Yes;"
        "Connection Timeout=30;"
        "Trusted_Connection=No;"
    )

    return pyodbc.connect(conn_str)
