import sqlite3
import datetime
import pytz
import psycopg2
import json

# a = "postgres://yejddozsfnklsi:7441bc9fb0c8aca1d40b3a994d82075f2e3724330eb3ed65b4213d4b97686f93@ec2-3-248-121-12.eu-west-1.compute.amazonaws.com:5432/df1tdsvbhu6ra8"
# db_connection = psycopg2.connect(a, sslmode='require')
# cur = db_connection.cursor()


def get_now():
    return datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d-%m-%Y')


# def check_user(user_id, username, first_name):
#     cur.execute(f"SELECT id FROM users WHERE id = {user_id}")
#     result = cur.fetchone()

#     if not result:
#         cur.execute("INSERT INTO users (id, username, first_name) VALUES (%s, %s, %s)",
#                     (user_id, username, first_name))
#         db_connection.commit()
#         return False
#     return True

locCon = sqlite3.connect('bot/local.db', check_same_thread=False)
cur = locCon.cursor()


def check_user(user_id, username, first_name):
    cur.execute(f"SELECT id FROM users WHERE id = '{user_id}'")
    result = cur.fetchone()

    if not result:
        cur.execute("INSERT INTO users (id, username, first_name) VALUES (?, ?, ?)",
                    (user_id, username, first_name))
        locCon.commit()
        return False
    return True


def v_wallet(user_id, wallet):
    cur.execute(f"SELECT wallet FROM users WHERE id = '{user_id}'")
    result = cur.fetchone()

    if result[0] == "none":
        cur.execute(
            f"UPDATE users SET wallet = '{wallet}' WHERE id = '{user_id}'")
        locCon.commit()
        return True
    else:
        return result[0]


def get_user_wallet(user_id):
    cur.execute(f"SELECT wallet FROM users WHERE id = '{user_id}'")
    result = cur.fetchone()
    return result[0]


def add_v_transaction(source, hash, value, comment):
    cur.execute("INSERT INTO transactions (source, hash, value, comment) VALUES (?, ?, ?, ?)",
                (source, hash, value, comment))
    locCon.commit()


def check_transaction(hash):
    cur.execute(f"SELECT hash FROM transactions WHERE hash = '{hash}'")
    result = cur.fetchone()
    if result:
        return True
    return False

# get list of transactions for wallet


def get_user_payments(user_id):
    wallet = get_user_wallet(user_id)

    if wallet == "none":
        return "You have no wallet"
    else:

        cur.execute(f"SELECT * FROM transactions WHERE source = '{wallet}'")
        result = cur.fetchall()
        tdict = {}
        tlist = []
        try:
            for transaction in result:
                tdict = {
                    "value": transaction[2],
                    "comment": transaction[3],
                }
                tlist.append(tdict)
            return tlist

        except:

            return False


print(get_now())
