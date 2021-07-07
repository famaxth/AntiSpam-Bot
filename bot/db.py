# - *- coding: utf- 8 - *-

#Production by Famaxth
#Telegram - @por0vos1k


import sqlite3

def ensure_connection(func):

    def decorator(*args, **kwargs):
        with sqlite3.connect('black_list.db') as conn:
            result = func(conn, *args, **kwargs)

        return result

    return decorator


@ensure_connection
def init_db(conn, force: bool = False):

    c = conn.cursor()

    if force:
        c.execute("DROP TABLE IF EXISTS users")

    c.execute("""CREATE TABLE IF NOT EXISTS black_list (
        id              INTEGER PRIMARY KEY,
        first_name                   STRING,
        last_name                    STRING,
        user_id                     STRING);
    """)

    conn.commit()



@ensure_connection
def add_user(conn, first_name: str, last_name: str, user_id):
    c = conn.cursor()

    c.execute("INSERT INTO black_list (first_name, last_name, user_id) VALUES (?, ?, ?)", (first_name, last_name, user_id))

    conn.commit()


@ensure_connection
def return_black_list(conn):
    c = conn.cursor()

    c.execute("SELECT user_id FROM black_list")

    all_results = c.fetchall()

    return all_results