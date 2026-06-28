import psycopg2
import os
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def create_database_connection():
    conn = psycopg2.connect(
        host=os.getenv("host"),
        database=os.getenv("database"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        port=os.getenv("port"),
    )

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("COnnected")
    return conn, cursor
