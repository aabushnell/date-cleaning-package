import pytest
import os
from sqlalchemy import text, create_engine
import sqlite3
from load_periodo import load_periodo

postgres_engine = "postgresql://user_longrungrowth:YjkqSNQ_CG6M25TKf@postgresql11.db.huma-num.fr/longrungrowth"

#local postgres
#engine = "postgresql://user_longrungrowth:YjkqSNQ_CG6M25TKf@localhost/longrungrowth"

db_created = False
path = os.path.dirname(os.path.realpath(__file__))

#sqlite
engine=f"sqlite:///{path}/DateCleaning.db"
def create_db():
    with open(path + "/create_sqlite_tables.sql", 'r') as sql_file:
        sql_script = sql_file.read()

    conn = sqlite3.connect(path + "/DateCleaning.db")
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    load_periodo(engine)
    conn.commit()
    #conn.close()

    db_created = True
    print("created sqlite for test")

def get_engine():
    if not db_created:
        create_db()
    return engine

def get_postgres_engine():
    return postgres_engine

