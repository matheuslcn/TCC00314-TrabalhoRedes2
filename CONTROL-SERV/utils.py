from socket import *
from collections import namedtuple
import time

import pandas
import sqlalchemy as sql

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

ch_tuple = namedtuple( 'ch_tup' , [ 'db_tuple' , 'time_stamp'] )

def init_cache( num ):

    global db_cache
    db_cache = dict()

    global ch_limit
    ch_limit = num

    global cache_full
    cache_full = lambda : len( db_cache ) >= ch_limit

def fetch_cache( key_tup ):

    ch_tup = db_cache.get( key_tup , None )
    if not( ch_tup is None ):
        ch_tup.time_stamp = time.time()
    return ch_tup[ 0 ]

def add_cache( key_tup , db_tup ):

    if cache_full():
        return False

    tup = fetch_cache( key_tup )
    if tup is None:
        db_cache[ key_tup ] = ch_tuple( 
            db_tuple   = db_tup,
            time_stamp = time.time()
        )
        return True
    
    return False

def remove_cache( key_tup ):

    tup = fetch_cache( key_tup )
    if not ( tup is None ):
        del db_cache[ key_tup ]
    return tup

def least_ru( ):

    '''
        retorna a entrada da cache com o menor time_stamp
    '''
    if len( db_cache ) == 0:
        return None

    foo = lambda x :db_cache[ x ].time_stamp
    return min( db_cache.keys() , key = foo )

def flush_cache( key_tup , conn ):

    db_num , db_key = key_tup
    db_tup = fetch_cache( key_tup ).db_tuple

    w_statement = write_stm( db_num , db_tup )
    d_statement = delet_stm( db_num , db_key )

    try:
        conn.execute( sql.text( w_statement ) )
    except sql.exc.DatabaseError:
        conn.execute( sql.text( d_statement ) )
        conn.execute( sql.text( w_statement ) )

def make_room( conn ):

    if cache_full():
        exit_key = least_ru()
        flush_cache( exit_key , conn )
        remove_cache( exit_key )
    
#--------------------------------------------------------------------
# Declarações para interagir com o SGBD.

def get_stm( db_num ):

    if db_num == CH_USR:
        stm = "user"

    elif db_num == CH_GRP:
        stm = "group"

    elif db_num == CH_MBR:
        stm = "membership"
    else:
        raise ValueError( "NAO EXISTE" )
    
    return stm

def select_stm( db_num , db_key ):
    
    stm = get_stm( db_num )
    return "SELECT * FROM " + stm + " WHERE name = {}".format( db_key )

def write_stm( db_num , db_tup ):

    stm = get_stm( db_num )    
    return "INSERT INTO " + stm + " VALUES ( {} , {} )".format( *db_tup )

def delet_stm( db_num , db_key ):

    stm = get_stm( db_num )
    return "DELETE FROM " + stm + " user WHERE name = {}".format( db_key )

#---------------------------------------------------------------------
# O objetivo das funçoes abaixo é de gerir a interação do servidor de
# controle com as tabelas do banco de dados

def write( key_tup , db_tup , conn , to_flush = False ):

    if not ( fetch_cache( key_tup ) is None ):
        remove_cache( key_tup )
    else:
        make_room( conn )
    
    add_cache( key_tup , db_tup )
    if to_flush:
        flush_cache( key_tup , conn )

def read( key_tup, conn ):

    db_tup = fetch_cache( key_tup )
    if db_tup is not None:
        return db_tup
    
    db_num , db_key = key_tup
    stm = select_stm( db_num , db_key )
    seq = conn.execute( sql.text( stm ) )
    if not seq:
        return None
    
    db_tup = seq[ 0 ]
    make_room( conn )
    add_cache( key_tup , db_tup )

    return db_tup

def delete( key_tup , conn ):

    if fetch_cache( key_tup ) is not None:
        remove_cache( key_tup )
    
    db_num , db_key = key_tup
    stm = delet_stm( db_num , db_key )
    conn.execute( sql.text( stm ) )

#-------------------------------------------------------------------------
# Essas funcoes serao a interface com o modulo main. As demais funcoes( acima 
# desse bloco ), Não devem ser usadas, são como uma caixa preta.

usr_tuple = namedtuple( 'usr_tuple' , [ 'name' , 'premium' ] )
grp_tuple = namedtuple( 'grp_tuple' , [ 'name' , 'owner'] )
mbr_tuple = namedtuple( 'mbr_tuple' , [ 'name' , 'u_name' , "g_name" ] )

def get_user_information( user ):

    key_tup = ( user , CH_USR )
    engine = sql.create_engine( 'sqlite:///CONTROL-SERV/controle.db')
    with engine.connect() as conn:
        return read( key_tup , conn )

def add_user( user , premium = False , flush = False ):

    key_tup = ( user , CH_USR )
    db_tup  = usr_tuple( name = user , premium = int( premium ) ) 
    engine = sql.create_engine( 'sqlite:///CONTROL-SERV/controle.db')
    with engine.connect() as conn:
        write( key_tup , db_tup , conn , to_flush = flush )

        

