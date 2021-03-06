# from socket import *
from collections import namedtuple
import time
import random
from string import ascii_lowercase
from typing import Text

# import pandas
import sqlalchemy as sql
from sqlalchemy import Table, Column, MetaData
from sqlalchemy.sql.expression import null
from sqlalchemy.pool import StaticPool


# def print_memo( fun ):

#     def prt_fun( *args, **kwargs ):

#         res = fun( *args , **kwargs )
#         print( res )
#         return res

#     return prt_fun

logged_users = []


def init_db_engine():
    global engine
    engine = sql.create_engine('sqlite:///CONTROL_SERV/controle.db', connect_args={'check_same_thread': False},
                               poolclass=StaticPool)
    # engine = sql.create_engine('sqlite:///controle.db')

    global conn
    conn = engine.connect()


def fetch_user(user_name):
    s = "SELECT * FROM \"user\" WHERE name = \"{}\"".format(user_name)
    seq = conn.execute(sql.text(s))
    return seq.first()


# @print_memo
def check_user(user_name):
    return not (fetch_user(user_name) is None)


# @print_memo
def create_user(user_name, premium=False):
    premium = int(premium)
    s = "INSERT INTO \"user\" values(\"{}\" , {} )".format(user_name, premium)
    conn.execute(sql.text(s))

    return "USER_CREATED_ACK"


# @print_memo
def get_user_information(user_name):
    s = "SELECT * FROM \"user\" WHERE name = \"{}\"".format(user_name)
    tup = conn.execute(sql.text(s)).first()

    user_ip = ''
    for user in logged_users:
        if user[0] == user_name:
            user_ip = user[1]

    msg = f"USER_INFORMATION {user_name} {user_ip} {bool(tup.premium)} "

    grupo = ver_grupo(user_name)
    if grupo != "":
        msg += grupo
    else:
        msg += ","
    return msg


def entrar_na_app(user_name):
    if not (check_user(user_name)):
        create_user(user_name)
        return "ENTRAR_NA_APP_ACK"

    return get_user_information(user_name)


def sair_da_app(user_name):
    s = "DELETE FROM \"user\" WHERE name = \"{}\"".format(user_name)
    conn.execute(sql.text(s))
    return "SAIR_DA_APP_ACK"


def is_user_premium(user_name):
    if not check_user(user_name):
        return False

    return bool(fetch_user(user_name).premium)


def criar_grupo(user_name):
    if not is_user_premium(user_name) or is_group_owner(user_name):
        return "CRIAR_GRUPO_NACK"

    s1 = "INSERT INTO \"group\" ( owner ) VALUES ( \"{}\" )".format(user_name)
    s2 = "INSERT INTO \"membership\" ( name , owner ) VALUES ( \"{}\" ,\"{}\" )".format(user_name, user_name)

    for s in [s1, s2]:
        conn.execute(sql.text(s))

    return "CRIAR_GRUPO_ACK"


def is_group_owner(user_name):
    s1 = "SELECT * FROM \"group\" WHERE owner = \"{}\"".format(user_name)
    seq = conn.execute(sql.text(s1))
    return seq.first() is not None


def add_grupo(owner_name, user_name):
    if not (is_user_premium(owner_name) and is_group_owner(owner_name)):
        return "ADD_USER_GRUPO_NACK"

    s = "INSERT INTO \"membership\" ( name , owner ) VALUES ( \"{}\" ,\"{}\" )".format(user_name, owner_name)
    conn.execute(sql.text(s))
    return "ADD_USER_GROUP_ACK"


def upgrade_user(user_name):
    if not check_user(user_name):
        return "UPGRADE_USER_NACK"

    s = "UPDATE \"user\" SET premium = 1 WHERE name = \"{}\" ".format(user_name)
    conn.execute(sql.text(s))
    return "UPGRADE_USER_ACK"


def remover_usr_grupo(owner_name, user_name):
    if not (is_user_premium(owner_name) and is_group_owner(owner_name)):
        return "RMV_USER_GRUPO_NACK"

    s = "DELETE FROM \"membership\" WHERE name = \"{}\"".format(user_name)
    conn.execute(sql.text(s))
    return "RMV_USER_GRUPO_ACK"


def get_grupo(owner_name):
    s = "SELECT name FROM \"membership\" WHERE owner = \"{}\"".format(owner_name)
    seq = conn.execute(sql.text(s))
    return [x.name for x in seq]


def ver_grupo(owner_name):
    if not (is_user_premium(owner_name) and is_group_owner(owner_name)):
        return ""

    seq = get_grupo(owner_name)
    return ",".join(x for x in seq)
