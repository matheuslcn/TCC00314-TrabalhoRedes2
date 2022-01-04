# from socket import *
from collections import namedtuple
import time
import random
from string import ascii_lowercase
from typing import Text

# import pandas
import sqlalchemy as sql
from sqlalchemy import engine
from sqlalchemy.sql.expression import false

# -------------------------------------------------------------------------
# É interessante ter um cache de usuários na memória do servidor para
# otimizar a performance das operações ao reduzir o numero de acessos
# ao banco de dados.
#
# Essa cache sera formada por um dicionario. Cada chave dessa cache será uma
# tupla contendo um numero representando a tabela do banco de dados e a chave
# de uma tupla da respectiva tabela. O valor correspondente sera uma tupla da
# tabela mais um timestamp de quando a chave foi consultada.

CH_USR = 0  # Cache para usuarios
CH_MBR = 1  # Para relação usuario ( pertence ) grupo
CH_GRP = 2  # Para grupos

ch_tuple = namedtuple('ch_tuple', ['db_tuple', 'time_stamp'])


def init_db_engine():

    global engine
    engine = sql.create_engine('sqlite:///CONTROL-SERV/controle.db')

def get_user_information( user_name ):

    with engine.connect as conn:

        s = "SELECT * FROM \"user\" WHERE name = {}".format( user_name )
        seq = conn.execute( sql.text( s ) )
        
        if not seq:
            return None
        
        return seq.first()
    
def entrar_na_app( user_name ):

    tup = get_user_information( user_name )
    pass

def sair_da_app( user_name ):
    
    with engine.connect as conn:
        s = "DELETE FROM \"user\" WHERE name = {}".format( user_name )
        conn.execute( sql.text( s ) )

    return "SAIR_DA_APP_ACK"

def is_user_premium( user_name ):

    tup = get_user_information( user_name )
    if tup is None:
        return False
    return bool( tup.premium )

def criar_grupo( user_name , group_name ):
    
    if not is_user_premium( user_name ):
        return "CRIAR_GRUPO_NACK"

    with engine.connect as conn:

        s1 = "INSERT INTO \"group\" ( name , owner ) VALUES ( \"{}\" ,\"{}\" )".format( group_name , user_name )
        s2 = "INSERT INTO \"membership\" ( user , group ) VALUES ( \"{}\" ,\"{}\" )".format( user_name , group_name )

        for s in [ s1 , s2 ]:
            conn.execute( sql.text( s ) )

    return "CRIAR_GRUPO_ACK"

def is_group_owner( owner_name , group_name ):
    pass

def add_grupo( owner_name, group_name, user_name ):
    
    if not ( is_user_premium( owner_name ) and is_group_owner( owner_name , group_name ) ):
        return "ADD_USER_GRUPO_NACK"
    
    with engine.connect as conn:
        s = "INSERT INTO \"membership\" ( user , group ) VALUES ( \"{}\" ,\"{}\" )".format( user_name , group_name )
        conn.execute( sql.text( s ) )
    return "ADD_USER_GROUP_ACK"

def remover_usr_grupo( owner_name, group_name, user_name ):
    
    if not ( is_user_premium( owner_name ) and is_group_owner( owner_name , group_name ) ):
        return "RMV_USER_GRUPO_NACK"
    
    with engine.connect as conn:
        s = "DELETE FROM \"membership\" WHERE user = \"{}\"".format( user_name )
        conn.execute( sql.text( s ) )

    return "RMV_USER_GRUPO_ACK"

def ver_grupo( owner_name, group_name ):
    
    if not ( is_user_premium( owner_name ) and is_group_owner( owner_name , group_name ) ):
        return ""
    
    with engine.connect as conn:
        s = "SELECT user FROM \"membership\" WHERE name = \"{}\"".format( group_name )
        seq = conn.execute( sql.text( s ) )
        return "\n".join( x for x in seq )

