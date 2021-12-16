import socket
import utils


HOST = '127.0.0.1'  # IP do servidor
SERVER_PORT = 5000  # Porta onde o servidor está escutando
STREAM_HOST = '127.0.0.1'  # IP do servidor de streaming
STREAM_PORT = 5555  # Porta do servidor com o streaming


def logout(user):
    """
    desloga o usuario
    :param user:
    :return 'SAIR_DA_APP_ACK':
    """
    print(user)
    return 'SAIR_DA_APP_ACK'


def get_user_information(user):
    """
    Pega todas as informacoes do usuario e envia para o servidor de streaming
    :param user:
    :return 'USER_INFORMATION' + ' ' + user_id:
    """
    # user_tup = utils.get_user_information( user )
    # if user_tup is None:
    #     return 'USER UNKNOWN'
    
    # name , premium = user_tup
    # return 'USER_INFORMATION {} {}'.format( name , bool( premium ))

    return 'USER_INFORMATION' + ' ' + 'user_id'


def login(user):
    """
    Se achar o usuario no bd, manda a mensagem 'STATUS_DO_USUARIO',
        informando ID, tipo de servico e membros do grupo.
    Caso contrario, cria um no bd e envia 'ENTRAR_NA_APP_ACK' com uma mensagem de confirmacao da criacao.
    :param user:
    :return 'STATUS_DO_USUARIO' + ' ' + user_id || 'ENTRAR_NA_APP_ACK'  :
    """

    # user_tup = utils.get_user_information( user )
    # if user_tup is None:
    #     utils.add_user( user )
    #     return 'ENTRAR_NA_APP_ACK'
    
    # name , premium = user_tup
    # return 'STATUS_DO_USUARIO {} {}'.format( name , bool( premium ))

    return 'STATUS_DO_USUARIO' + ' ' + 'user_id'


def connection_manager(conn):

    with conn:
        data_byte = conn.recv(1024)
        data_string = data_byte.decode()
        data = data_string.split(" ")

        if data[0] == 'GET_USER_INFORMATION':
            message = get_user_information(data[1])
        elif data[0] == 'ENTRAR_NA_APP':
            message = login(data[1])
        elif data[0] == 'SAIT_DA_APP':
            message = logout(data[1])

        conn.sendall(message.encode())


# Cria o soquete do servidor com o streaming e comeca a ouvir
server_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_stream_socket.bind((HOST, STREAM_PORT))
server_stream_socket.listen()
print("Esperando conexão o Streaming...")

# Aceita a conexao com o streaming
stream_connection, stream_ip = server_stream_socket.accept()
print('GOT CONNECTION FROM:', stream_ip)

# Cria o soquete para os clientes e comeca a ouvir
server_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_client_socket.bind((HOST, SERVER_PORT))
server_client_socket.listen()
print('Esperando conexão do cliente...')


# Aceita uma conexao com o cliente
while True:
    client_connection, client_ip = server_client_socket.accept()
    print('GOT CONNECTION FROM:', client_ip)
    connection_manager(client_connection)

    connection_manager(stream_connection)
