import socket
import threading

LOCAL_HOST = '127.0.0.1'    # localhost
SERVER_HOST = '127.0.0.1'   # IP do servidor
STREAM_HOST = '127.0.0.1'   # IP do stream
CLIENT_TCP_PORT = 6060  # Porta do cliente
CLIENT_UDP_PORT = 5001  # Porta onde o cliente vai se comunicar com o servidor de streaming
SERVER_PORT = 5000      # Porta usada pelo servidor
STREAM_PORT = 6000      # Porta usada pelo servidor de streaming


def login():
    """
    faz o login do usuario no servico
    :return:
    """
    print("login\n")
    client_streaming_socket.sendto('LISTAR_VIDEOS'.encode(), (STREAM_HOST, STREAM_PORT))


def sign_in():
    """
    mostra na tela q o usuario foi cadastrado e entrar na app
    :return:
    """
    print('usuario cadastrado\n')
    login()


def status(user):
    """
    mostra na tela as informacoes recebidas do usuario
    :return:
    """
    print("status\n")
    login()


def video_list(videos):
    """
    lista os videos recebidos do servidor de streaming
    :return:
    """
    print("video_list\n")
    print(videos)
    return


def tcp_connection():
    while True:
        data_byte = client_server_socket.recv(1024)
        data_string = data_byte.decode()
        data = data_string.split(' ')

        if data[0] == 'ENTRAR_NA_APP_ACK':
            sign_in()
        elif data[0] == 'STATUS_DO_USUARIO':
            status(data[1])
        elif data[0] == 'SAIR_DA_APP_ACK':
            client_server_socket.close()
            client_streaming_socket.close()


def udp_connection():
    while True:
        print("esperando mensagem do streaming...")
        m = client_server_socket.recvfrom(1024)
        print("chegou mensagem do streaming!")
        data_byte = m[0]
        data_string = data_byte.decode()
        data = data_string.split(' ')
        if data[0] == 'LISTA_DE_VIDEOS':
            video_list(data[1])


if __name__ == "__main__":
    # Criacao e conexao do soquete do servidor
    client_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_server_socket.bind((LOCAL_HOST, CLIENT_TCP_PORT))
    client_server_socket.connect((SERVER_HOST, SERVER_PORT))

    # Criacao do soquete de comunicacao com o streaming
    client_streaming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_streaming_socket.bind((LOCAL_HOST, CLIENT_UDP_PORT))

    # Tentativa de login
    username = input("digite o usuario:")
    message = 'ENTRAR_NA_APP' + ' ' + username + ' ' + 'ip'  # Estou usando ' ' como separador dos arqgumentos
    client_server_socket.sendall(message.encode())

    server_conn = threading.Thread(target=tcp_connection)
    streaming_conn = threading.Thread(target=udp_connection)
    server_conn.start()
    streaming_conn.start()
