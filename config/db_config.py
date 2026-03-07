import os

DB_CONN_PARAMS = {
        "dbname": "my-shows-rating",
        "user": "postgres",
        "password": os.getenv("DB_PASSWORD"),
        "host": "127.0.0.1",
        "port": "5432"
    }