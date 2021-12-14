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
mbr_tuple = namedtuple( 'mbr_tuple' , [ 'usr_name' , "grp_name" ] )

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

    cache_tup = ( tup, new_tup, time.time() )
    ch[ nome ] = cache_tup

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

def pop_cache( ch_num = CH_USR ):

    ch = select_cache( ch_num )
    if ch is None:
        raise ValueError( "ESSE CACHE NAO EXISTE")
    
    foo = lambda x : ch[ x ][ 2 ]
    lru_key = min( ch.keys , foo )
    tup , altered , _ = ch[ lru_key ]

    del ch[ lru_key ]
    return tup , altered

def make_room( conn , ch_num = CH_USR  ):
    
    tup , altered = pop_cache( ch_num )
    if altered:

        s = "INSERT INTO user VALUES ( {} , {} )"
        if ch_num == CH_MBR:
            s = "INSERT INTO membership VALUES ( {} , {} )"
        elif ch_num == CH_GRP:
            s = "INSERT INTO group VALUES ( {} , {} )"
        
        conn.execute( sql.text( s.format( *tup ) ) )


#---------------------------------------------------------------------
# O objetivo das funçoes abaixo é de gerir a interação do servidor de
# controle com a tabela de usuarios no servidor. Cada entrada dessa tabela
# é indexada pelo seu hash, mas cada usuario prefere se identificar pelo
# seu nome. Cada uma dessas funções també tem o argumento conn, que é um
# sqlalchemy.Connection para o banco de dados do servidor.

def fetch_user( user_name , conn ):
    
    #-----------------------------------------------------
    # procurando primeiro no cache. Se existir, é 
    # só devolver
    tup = fetch_cache( user_name )
    if tup is None:
    
        seq = conn.execute( sql.text(
            '''
            SELECT name , premium FROM user
            WHERE nome = {}
            '''.format( user_name )
        ) )

        if not seq:
            return None
        
        if cache_full():
            make_room( conn , CH_USR )
        
        tup = seq[ 0 ]
        add_cache( user_name , tup )
    return tup

def add_user( user_name , conn , premium = False ):
    
    #-----------------------------------------------------
    # Para evitar duplicatas, ver se o usario ja existe no
    # BD.
    if fetch_user( user_name , conn ) is not None:
        print( "usuario ja existe")
        return
    
    #---------------------------------------------------
    # usuario nao existe, entao é safo criar novo. Contudo
    # vamos adiciona-lo só na cache. E sera mandado somente
    # quando for dado espaço na cache.
    usr = usr_tuple(
        nome    = user_name,
        premium = int( premium )
    )

    add_cache( user_name , usr, new_tup = True )


def rmv_user( user_name , conn ):
    pass

def upgrade_user( user_name , conn ):
    pass

group_tuple = namedtuple( 'group_tuple' , [ 'nome' , 'id' , 'dono' ] )

def db_fetch_group( group_name, conn ):
    
    # o hash do nome é a chave primaria
    h = hash( group_name )

    pass

def db_add_group( group_name, group_owner , conn ):
    pass

def db_rmv_group( group_name , conn ):
    pass

cache_group_tuple = namedtuple( 'cache_group_tuple' , [ 'group_tuple' , 'altered' ] )

def init_group_cache( num ):
    pass

def group_cache_full():
    pass

def cache_fetch_group( group_name ):
    
    # o hash do nome é a chave primaria
    h = hash( group_name )

    pass

def cache_add_group( group_name , owner ):
    pass

def cache_rmv_group( group_name ):
    pass
