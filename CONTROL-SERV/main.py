import socket
import utils
import threading


HOST = '127.0.0.1'          # IP do servidor
SERVER_PORT = 5000          # Porta onde o servidor está escutando
STREAM_HOST = '127.0.0.1'   # IP do servidor de streaming
STREAM_PORT = 5555          # Porta do servidor com o streaming

def init_logs():

    global logged_users
    logged_users = set()

def logout( user_name ):
    """
    desloga o usuario
    :param user:
    :return 'SAIR_DA_APP_ACK':
    """

    logged_users.remove( user_name )
    return 'SAIR_DA_APP_ACK'

def login( user_name ):

    """
    Se achar o usuario no bd, manda a mensagem 'STATUS_DO_USUARIO',
        informando ID, tipo de servico e membros do grupo.
    Caso contrario, cria um no bd e envia 'ENTRAR_NA_APP_ACK' com uma mensagem de confirmacao da criacao.
    :param user:
    :return 'STATUS_DO_USUARIO {user} {bool(premium)}' ou 'ENTRAR_NA_APP_ACK'  :
    """
    if user_name in logged_users:
        return 'USUARIO_JA_LOGADO'
    logged_users.add( user_name )
    return utils.entrar_na_app( user_name )

def get_user_information( user_name ):
    """
    Pega todas as informacoes do usuario e envia para o servidor de streaming
    :param user:
    :return 'USER_INFORMATION {user} {boll(premium)}':
    """
    return utils.get_user_information( user_name )
    


def create_connection(host, port):
    """
    Cria um socket TCP e espera conexoes com clientes, quando uma conexao é aceita,
    cria uma thread para o cliente para troca de mensagens
    :param host:
    :param port:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    while True:
        print("Esperando conexao...")
        conn, ip = s.accept()
        print('GOT CONNECTION FROM:', ip)
        thread = threading.Thread(target=threaded_client, args=(conn,))
        thread.start()


def threaded_client(conn):
    """
    Espera receber uma mensagem do cliente e chama uma funcao diferente para cada tipo de mensagem
    :param conn:
    :return:
    """
    
    client_name = ''
    while conn:
        data_byte = conn.recv(1024)
        data_string = data_byte.decode()
        data = data_string.split(" ")

        msg = data[0]

        if   msg == 'GET_USER_INFORMATION':
            message = get_user_information(data[1])

        elif msg == 'ENTRAR_NA_APP':
            message = login(data[1])
            client_name = data[1]

        elif msg == 'SAIR_DA_APP':
            message = logout( client_name )
        
        elif msg == 'CRIAR_GRUPO':
            message = utils.criar_grupo( client_name )
        
        elif msg == 'ADD_USUARIO_GRUPO':
            message = utils.add_grupo( client_name , data[ 1 ] )
        
        elif msg == 'REMOVER_USUARIO_GRUPO':
            message = utils.remover_usr_grupo( client_name , data[ 1 ] )
        
        elif msg == 'VER_GRUPO':
            message = utils.ver_grupo( client_name )

        else:
            print("Mensagem invalida")
            continue
        conn.sendall(message.encode())

        if msg == 'SAIR_DA_APP':
            return


def main():
    """
    cria duas threads, uma para a conexao com o servidor de streaming
    e outra para a conexao com os clientes
    :return:
    """

    utils.init_db_engine()
    stream_thread = threading.Thread(target=create_connection, args=(STREAM_HOST, STREAM_PORT))
    stream_thread.start()
    client_thread = threading.Thread(target=create_connection, args=(HOST, SERVER_PORT))
    client_thread.start()


if __name__ == "__main__":
    main()
