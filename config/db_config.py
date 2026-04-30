import os

DB_CONN_PARAMS = {
    "dbname": os.getenv("POSTGRES_DB", "my-shows-rating"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}
