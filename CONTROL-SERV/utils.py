from socket import *
from collections import namedtuple
import time
import random
from string import ascii_lowercase

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

ch_tuple = namedtuple( 'ch_tuple' , [ 'db_tuple' , 'time_stamp'] )

def init_cache( num ):

    '''
        Como o proprio nome ja diz, inicializa o cache do BD. 
        num é o numero maximo de elementos do cache.
        Deve ser chamado sempre que o servidor de controle estiver no ar.
    '''

    #----------------------------------------------------------------------
    # È um unico cache unificado para as tres tabelas.
    global db_cache
    db_cache = dict()

    global ch_limit
    ch_limit = num

    #---------------------------------------------------------------------
    # Toda vez que tenta inserir uma tupla no cache, verifica se o cache está
    # cheio. Se sim, então deve-se remover um elemento do cache e escrever no
    # banco de dados.
    global cache_full
    cache_full = lambda : len( db_cache ) >= ch_limit

def fetch_cache( key_tup ):

    '''
        Retorna o elemento correspondente a key_tup no cache,
        se esse existir. Caso exista, seu timestamp precisa ser
        atualizado. Retorna None se não estiver.
    '''

    #---------------------------------------------
    # Fazendo uma busca direta
    ch_tup = db_cache.get( key_tup , None )

    #----------------------------------------------------------------
    # Caso a tupla exista, deve-se se atualizar o timestamp. Como named
    # tuples não podem ser alteradas, deve-se criar uma nova tupla. 
    if not( ch_tup is None ):
        new_tup = ch_tuple(
            db_tuple = ch_tup.db_tuple,
            time_stamp = time.time()
        )
        db_cache[ key_tup ] = new_tup

    return ch_tup

def add_cache( key_tup , db_tup ):

    '''
        Tenta adicionar uma nova entrada no cache, e retorna verdadeiro se
        conseguir. As condições são: O cache não deve estar cheio, e a chave não 
        deve existir antes.
    '''

    if cache_full():
        return False

    tup = fetch_cache( key_tup )
    if tup is None:
        db_cache[ key_tup ] = ch_tuple( 
            db_tuple   = db_tup,
            time_stamp = time.time()
        )
        return True
    
    #---------------------------------------------------------
    # Se chegou aqui, é porque key_tup ja existia na cache.
    return False

def remove_cache( key_tup ):
    
    '''
        Remove e retorna a entrada correspondente a key_tup. 
    '''

    tup = fetch_cache( key_tup )
    if not ( tup is None ):
        del db_cache[ key_tup ]
    return tup

def least_ru( ):

    '''
        retorna a chave da cache com o menor time_stamp, isso é importante
        por que quanto menor o valor do time_stamp, menor a chance da entra-
        da ser consultada no futuro. Podendo assim ser removida da cache sem
        muitos problemas
    '''

    if len( db_cache ) == 0:
        return None

    foo = lambda x :db_cache[ x ].time_stamp
    return min( db_cache.keys() , key = foo )

def flush_cache( key_tup , conn ):

    '''
        Copia a entrada do cache para o banco de dados.

        Essa funcao nunca é chamada diretamente, mas sim por
        funcoes que antes testam se a entrada está na cache.
    '''

    #---------------------------------------------------------
    # O fetch nã será testado, pois ja se assume que a entrada
    # ja esteja na cache
    db_key , db_num = key_tup
    db_tup = fetch_cache( key_tup ).db_tuple

    #---------------------------------------------------------
    # Gera os Sql statements necessários para operar com o banco de
    # dados. Por preucauçao, cria o delete junto com o write
    w_statement = write_stm( db_num , db_tup )
    d_statement = delet_stm( db_num , db_key )

    conn.execute( sql.text( w_statement) )
    try:

        #---------------------------------------------------------
        # Tenta primeiro só escrever, se tiver duplicata, gera excessão
        conn.execute( sql.text( w_statement) )

    except sql.exc.DatabaseError:

        #------------------------------------------------------------
        # Se cheagr aqui, é por que tem duplicata. Deve então remover
        # a duplicata para escrever a versão que tem na cache. Sim, Sim
        # é melhor usar o update, mas quando tentei deu muito problema,
        # então é melhor usar um hard overwrite.
        conn.execute( sql.text( d_statement) )
        conn.execute( sql.text( w_statement) )


def make_room( conn ):
    
    '''
        Remover a entrada mais antiga, e escreve - la no SGBD.
    '''

    exit_key = least_ru()               # Entrada a mais tempo sem ser consultada
    flush_cache( exit_key , conn )      # Mandar para o banco de dados
    remove_cache( exit_key )            # Remover

def drop_cache( ):

    '''
        Essa funcao é MUITO importante. Sempre usar antes de fechar o servidor, o que ela faz
        é esvaziar a cache e escrever o conteudo de cada tupla no BD. Se não for usada, há pos-
        sibilidade de dados novos nao serem salvos quando estiver terminado.
    '''
    engine = sql.create_engine( 'sqlite:///CONTROL-SERV/controle.db')
    with engine.connect() as conn:
        while len( db_cache ) > 0:
            make_room( conn )
    
#--------------------------------------------------------------------
# Declarações para interagir com o SGBD.

def get_stm( db_num ):

    '''
        Aqui so retorna o nome da tabela e o nome das variaveis para cada
        db_num
    '''

    if db_num == CH_USR:
        stm = ( "user" , "name" , "premium" )

    elif db_num == CH_GRP:
        stm = ( "group" , "name" , "owner" )

    elif db_num == CH_MBR:
        stm = ( "membership" , "name" , "u_name" , "g_name" )
    else:
        raise ValueError( "NAO EXISTE" )
    
    return stm

#----------------------------------------------------------------
# Statements para sql select
def select_stm( db_num , db_key ):
    
    stm = get_stm( db_num )
    return "SELECT * FROM " + stm[ 0 ] + " WHERE name = \"{}\"".format( db_key )

#-------------------------------------------------------------------
# Para sql write
def write_stm( db_num , db_tup ):

    stm = get_stm( db_num )    
    if db_num == CH_GRP:
        return "INSERT INTO " + "\"{}\" ( {} , {} )".format( *stm ) + " VALUES ( \"{}\" , \"{}\" )".format( *db_tup )
    return "INSERT INTO " + "{} ( {} , {} )".format( *stm ) + " VALUES ( \"{}\" , {} )".format( *db_tup )

#-------------------------------------------------------------------
# finalmente, para sql delete
def delet_stm( db_num , db_key ):

    stm = get_stm( db_num )
    return "DELETE FROM " + stm[ 0 ] + " WHERE name = \"{}\"".format( db_key )

#---------------------------------------------------------------------
# O objetivo das funçoes abaixo é de gerir a interação do servidor de
# controle com as tabelas do banco de dados. É baseado na sintaxe abstrata
# de transaçoes que eu apendi em BD2
def write( key_tup , db_tup , conn , to_flush = False ):

    '''
        Escreve a tupla e a entrada na sua tabela respectiva. Garante 
        que os dados escritos estarão ao menos na cache após a escrita.
        
        a variavel to_flush indica que o que foi escrito na cache deve ser
        imediatamente escrito no banco de dados. Se for false, o conteudo
        vai ser eventualmente escrito quando a função make_room ou drop cache
    '''

    #--------------------------------------------------------------------
    # Primeiro verifica se o a entrada ja esta na cache (  lembrando , 
    # a chave da cache é uma tupla com o numero correspondente a tabela
    # mais o valor da primary key da entrada do bd ). Se ja estiver, assume
    # duplicata e discarda a entrada antiga
    if not ( fetch_cache( key_tup ) is None ):
        remove_cache( key_tup )

    #--------------------------------------------------------------------
    # Mesmo sem duplicata, a cache pode estar cheia. Então antes deve-se abrir
    # espaço
    elif cache_full():
        make_room( conn )
    
    add_cache( key_tup , db_tup )             # Escreve na cache
    if to_flush:
        flush_cache( key_tup , conn )         # Escreve no BD

def read( key_tup, conn ):

    #------------------------------------------------------------------
    # Faz busca na cache, se existir, nem precisa fazer busca no BD
    db_tup = fetch_cache( key_tup )
    if db_tup is not None:
        return db_tup
    
    db_key , db_num = key_tup
    stm = select_stm( db_num , db_key )
    seq = conn.execute( sql.text( stm ) )
    if not seq:
        return None
    
    #------------------------------------------------------------------
    # Se chegou aqui, a entrada estava no BD mas nao na cache. Escrever na
    # cache para agilizar buscas futuras.
    db_tup = seq.first()
    if cache_full():
        make_room( conn )
    add_cache( key_tup , db_tup )

    return db_tup

def delete( key_tup , conn ):

    #-----------------------------------------------------
    # Caso tenha uma copia na cache
    if fetch_cache( key_tup ) is not None:
        remove_cache( key_tup )
    

    db_num , db_key = key_tup
    stm = delet_stm( db_num , db_key )
    conn.execute( sql.text( stm ) )

#-------------------------------------------------------------------------
# Essas funcoes serao a interface com o modulo main. As demais funcoes( acima 
# desse bloco ), Não devem ser usadas, são como uma caixa preta. Fique livre para adicionar 
# mais funcoes conforme for o necessário

#---------------------------------------------------------------------------
# Se key_tup era a chave do cache, os valores correspondentes contem uma des-
# sas tuplas e um timestamp.
usr_tuple = namedtuple( 'usr_tuple' , [ 'name' , 'premium' ] )
grp_tuple = namedtuple( 'grp_tuple' , [ 'name' , 'owner'] )
mbr_tuple = namedtuple( 'mbr_tuple' , [ 'name' , 'u_name' , "g_name" ] )

def get_user_information( user ):

    key_tup = ( user , CH_USR )
    engine = sql.create_engine( 'sqlite:///CONTROL-SERV/controle.db')
    with engine.connect() as conn:
        usr_info =  read( key_tup , conn )
        if usr_info is not None:
            nome , premium = usr_info
            usr_info = ( nome , bool( premium ) )
        return usr_info

def add_user( user , premium = False , flush = False ):

    key_tup = ( user , CH_USR )
    db_tup  = usr_tuple( name = user , premium = int( premium ) ) 
    engine = sql.create_engine( 'sqlite:///CONTROL-SERV/controle.db')
    with engine.connect() as conn:
        write( key_tup , db_tup , conn , to_flush = flush )

def add_group( owner , group_name , flush = False ):

    engine = sql.create_engine( 'sqlite:///CONTROL-SERV/controle.db')
    with engine.connect() as conn:

        #-------------------------------------------------------
        # consultando se o dono é um usuário premium
        usr_info = get_user_information( owner )
        if usr_info is None:
            raise ValueError( "USUARIO NAO EXISTE")

        _ , premium = usr_info
        if not premium:
            raise ValueError( "USUARIO NAO PREMIUM" )
        
        #------------------------------------------------------
        # Se chegou aqui então ok. Criando o grupo
        group = grp_tuple( group_name , owner )
        key_tup = ( group_name , CH_GRP )
        write( key_tup , group , conn , to_flush = True )
        
if __name__ == "__main__":

    init_cache( 10 )

    # add_user( "rafa123", premium = True, flush = True )
    # print( get_user_information( "rafa123" ) )

    # for x in range( 10 ):
    #     user = ''.join( random.choices( ascii_lowercase , k = 5 ) )
    #     add_user( user )
    # user = ''.join( random.choices( ascii_lowercase , k = 5 ) )
    # add_user( user )

    # for x in range( 10 ):
    #     user = ''.join( random.choices( ascii_lowercase , k = 5 ) )
    #     add_user( user )
    # drop_cache()

    add_group( "rafa123" , "acadCHAD", flush = True)