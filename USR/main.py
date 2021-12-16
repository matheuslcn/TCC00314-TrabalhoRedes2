import socket

LOCAL_HOST = '127.0.0.1'  # localhost
SERVER_HOST = '127.0.0.1'  # IP do servidor
STREAM_HOST = '127.0.0.1'  # IP do stream
CLIENT_PORT = 6060  # Porta do cliente
SERVER_PORT = 5000  # Porta usada pelo servidor
STREAM_PORT = 5050  # Porta onde o cliente vai se comunicar com o servidor de streaming


def login():
    """
    mostra na tela q o usuario foi cadastrado e entrar na app
    :return:
    """
    return


def status():
    """
    mostra na tela as informacoes recebidas do usuario
    :return:
    """
    return


def video_list():
    """
    lista os videos recebidos do servidor de streaming
    :return:
    """
    return


# Criacao e conexao do soquete do servidor
client_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_server_socket.bind((LOCAL_HOST, CLIENT_PORT))
client_server_socket.connect((SERVER_HOST, SERVER_PORT))

# Criacao do soquete de comunicacao com o streaming
client_streaming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Tentativa de login
message = 'ENTRAR_NA_APP' + ' ' + 'username' + ' ' + 'ip'  # Estou usando ' ' como separador dos arqgumentos
client_server_socket.sendall(message.encode())

isLogged = True
while isLogged:
    data_byte = client_server_socket.recv(1024)
    data_string = data_byte.decode()
    data = data_string.split(' ')

    if data[0] == 'ENTRAR_NA_APP_ACK':
        login()
    elif data[0] == 'STATUS_DO_USUARIO':
        status()
    elif data[0] == 'SAIR_DA_APP_ACK':
        isLogged = False
    elif data[0] == 'LISTA_DE_VIDEOS':
        video_list()
