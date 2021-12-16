from socket import *
from collections import namedtuple
import time

import pandas
import sqlalchemy as sql

# -------------------------------------------------------------------------
# É interessante ter um cache de usuários na memória do servidor para
# otimizar a performance das operações ao reduzir o numero de acessos
# ao banco de dados.

CH_USR = 0  # Cache para usuarios
CH_MBR = 1  # Para relação usuario ( pertence ) grupo
CH_GRP = 2  # Para grupos

usr_tuple = namedtuple( 'usr_tuple' , [ 'name' , 'premium' ] )
grp_tuple = namedtuple( 'grp_tuple' , [ 'name' , 'owner'] )
mbr_tuple = namedtuple( 'mbr_tuple' , [ 'u_name' , "g_name" ] )

def init_cache( num ):
    
    global user_cache, group_cache, member_cache
    user_cache = dict()
    group_cache = dict()
    member_cache = dict()

    global ch_limit
    ch_limit = num

def select_cache( ch_num = CH_USR ):

    ch = None
    if ch_num == CH_USR:
        ch = user_cache
    elif ch_num == CH_MBR:
        ch = member_cache
    elif ch_num == CH_GRP:
        ch = group_cache
    
    return ch

def cache_full( ch_num = CH_USR ):
    
    ch = select_cache( ch_num )
    if ch is None:
        return False
    return len( ch ) >= ch_limit

def add_cache( nome, tup, new_tup = False, ch_num = CH_USR ):

    '''
    se new_tup for verdadeiro, significa que a tupla foi criada pelo servidor
    e nao tem uma entrada equivalente na tabela.
    '''

    new_tup = int( new_tup )

    ch = select_cache( ch_num )
    if ch is None:
        raise ValueError( "ESSE CACHE NAO EXISTE")
    
    if cache_full( ch ):
        return False
    
    cache_tup = ( tup, new_tup, time.time() )
    ch[ nome ] = cache_tup
    return True

def fetch_cache( nome , ch_num = CH_USR ):

    ch = select_cache( ch_num )
    if ch is None:
        raise ValueError( "ESSE CACHE NAO EXISTE")
    
    cache_tup = ch.get( nome , None )
    if cache_tup is None:
        # raise ValueError( "ESSA ENTRADA EXISTE NO CACHE")
        return None
    
    tup , altered , _ = cache_tup
    ch[ nome ] = ( tup , altered , time.time() )

    return tup

def in_cache( nome , ch_num = CH_USR ):

    try:
        return not( fetch_cache ) is None
    except ValueError:
        return False

def pop_cache( ch_num = CH_USR ):

    ch = select_cache( ch_num )
    if ch is None:
        raise ValueError( "ESSE CACHE NAO EXISTE")
    
    foo = lambda x : ch[ x ][ 2 ]
    lru_key = min( ch.keys , foo )
    tup , altered , _ = ch[ lru_key ]

    del ch[ lru_key ]
    return lru_key , tup , altered

#--------------------------------------------------------------------
# Declarações para interagir com o SGBD.
def select_stm( tup_name , db_num = CH_USR ):
    
    if db_num == CH_USR:
        pass
    elif db_num == CH_GRP:
        pass
    elif db_num == CH_MBR:
        pass
    else:
        raise ValueError( "NAO EXISTE" )
    
    return s

def add_stm( tup , db_num = CH_USR ):
    pass

def alter_stm( tup , db_num = CH_USR ):
    pass

def remv_stm( tup , db_num = CH_USR ):
    pass

#---------------------------------------------------------------------
# O objetivo das funçoes abaixo é de gerir a interação do servidor de
# controle com as tabelas do banco de dados
def fetch_db( tup_name , conn , db_num = CH_USR ):
    pass

def add_db( tup_name , tup , conn , db_num = CH_USR ):
    pass

def remove_db( tup_name , tup , conn , db_num = CH_USR ):
    pass

def alter_db( tup_name , tup , conn , db_num = CH_USR ):
    pass