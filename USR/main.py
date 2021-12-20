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
    login()


def video_list(videos):
    """
    lista os videos recebidos do servidor de streaming
    :return:
    """
    print(videos)
    return


def tcp_message():
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


def udp_message():
    while True:
        stream_message = client_streaming_socket.recvfrom(1024)
        data_byte = stream_message[0]
        data_string = data_byte.decode()
        data = data_string.split(' ')
        if data[0] == 'LISTA_DE_VIDEOS':
            video_list(data[1])


if __name__ == "__main__":
    # Criacao e conexao do soquete do servidor
    client_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_server_socket.bind((LOCAL_HOST, CLIENT_TCP_PORT))
    client_server_socket.connect((SERVER_HOST, SERVER_PORT))
    username = input("digite o usuario:")
    message = f'ENTRAR_NA_APP {username} {socket.gethostname()}'
    client_server_socket.sendall(message.encode())
    server_conn = threading.Thread(target=tcp_message)
    server_conn.start()

    # Criacao e conexao do soquete de comunicacao com o streaming
    client_streaming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_streaming_socket.bind((LOCAL_HOST, CLIENT_UDP_PORT))
    streaming_conn = threading.Thread(target=udp_message)
    streaming_conn.start()


