from fastapi import FastAPI
from psycopg2 import pool
import psycopg2
import os
import time

app = FastAPI()

connection_pool = None

def init_pool():

    global connection_pool

    retries = 10

    while retries > 0:

        try:

            connection_pool = psycopg2.pool.SimpleConnectionPool(

                1,
                10,

                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")

            )

            return

        except Exception:

            retries -= 1

            time.sleep(3)

    raise Exception("DB pool failed")

@app.on_event("startup")

def startup():

    init_pool()

def get_connection():

    return connection_pool.getconn()

def release_connection(conn):

    connection_pool.putconn(conn)

@app.get("/health")

def health():

    try:

        conn = get_connection()

        release_connection(conn)

        return {
            "status":"ok",
            "db":"pool ok"
        }

    except:

        return {
            "status":"error"
        }
