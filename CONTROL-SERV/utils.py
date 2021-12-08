from socket import *
from collections import namedtuple
import time

import pandas
import sqlalchemy as sql

#---------------------------------------------------------------------
# O objetivo das funçoes abaixo é de gerir a interação do servidor de
# controle com a tabela de usuarios no servidor. Cada entrada dessa tabela
# é indexada pelo seu hash, mas cada usuario prefere se identificar pelo
# seu nome. Cada uma dessas funções també tem o argumento conn, que é um
# sqlalchemy.Connection para o banco de dados do servidor.

# É interessante ter um cache de usuários na memória do servidor para
# otimizar a performance das operações ao reduzir o numero de acessos
# ao banco de dados.

cache_usr_tuple = namedtuple( 'cache_usr_tuple' , [ 'usr_tuple' , 'altered' ] )
usr_tuple = namedtuple( 'usr_tuple' , [ 'nome' , 'hash' , 'premium' ] )

def init_cache( num ):
    
    global user_cache, group_cache, member_cache
    user_cache = dict()
    group_cache = dict()
    member_cache = dict()

    global ch_limit
    ch_limit = num

def user_cache_full( cnum ):
    return len( user_cache ) >= user_cache_limit

def make_room():
    pass

def fetch_user( user_name , conn ):
    
    #-----------------------------------------------------
    # procurando primeiro no cache. Se existir, é 
    # só devolver
    cusr = user_cache.get( user_name , None )
    if cusr is None:
    
        seq = conn.execute( sql.text(
            '''
            SELECT nome , hash , premium FROM USER
            WHERE NOME = {}
            '''.format( user_name )
        ) )

        if not seq:
            return None
        
        usr = seq[ 0 ]
        cusr = cache_usr_tuple( 
            usr,
            False
        )

        # if user_cache_full():
        #     usr_mkroom()
        user_cache[ user_name ] = cusr
    return cusr.usr_tuple

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
        premium = premium
    )

    cusr = cache_usr_tuple(
        user_tuple = usr,
        altered = True    # quando for removida da cache para dar espaço para novas entradas
    )

    user_cache[ user_name ] = cusr

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
