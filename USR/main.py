import socket
import threading

LOCAL_HOST = '127.0.0.1'  # localhost
SERVER_HOST = '127.0.0.1'  # IP do servidor
STREAM_HOST = '127.0.0.1'  # IP do stream
CLIENT_TCP_PORT = 6060  # Porta do cliente
CLIENT_UDP_PORT = 5001  # Porta onde o cliente vai se comunicar com o servidor de streaming
SERVER_PORT = 5000  # Porta usada pelo servidor
STREAM_PORT = 6000  # Porta usada pelo servidor de streaming


def login():
    """
    faz o login do usuario no servico e pede a lista de videos ao servidor de streaming
    :return:
    """
    client_streaming_socket.sendto('LISTAR_VIDEOS'.encode(), (STREAM_HOST, STREAM_PORT))
    print(f"LISTAR_VIDEOS enviado para o servidor de streaming")


def sign_in():
    """
    mostra na tela q o usuario foi cadastrado e entrar na app
    :return:
    """
    print('usuario cadastrado\n')
    login()


def status(user, is_premium):
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
    """
    É a função responsável pelo recebimento e processamento de mensagens do servidor de gerenciamento
    :return:
    """
    while client_server_socket:
        data_byte = client_server_socket.recv(1024)
        print(f"{data_byte} recebido do servidor de gerenciamento")
        data_string = data_byte.decode()
        data = data_string.split(' ')

        if data[0] == 'ENTRAR_NA_APP_ACK':
            sign_in()
        elif data[0] == 'STATUS_DO_USUARIO':
            status(data[1], data[2])
        elif data[0] == 'SAIR_DA_APP_ACK':
            client_server_socket.close()
            client_streaming_socket.close()
            print("deslogado")


def udp_message():
    """
    É a função responsável pelo recebimento e processamento de mensagens do servidor de streaming
    :return:
    """
    while client_streaming_socket:
        stream_message = client_streaming_socket.recvfrom(1024)
        print(f"{stream_message[0]} recebida do servidor de streaming")
        data_byte = stream_message[0]
        data_string = data_byte.decode()
        data = data_string.split(' ')
        if data[0] == 'LISTA_DE_VIDEOS':
            video_list(data[1])


def upload_video(video):
    print(video)
    return


if __name__ == "__main__":
    # Criacao e conexao do soquete do servidor
    client_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_server_socket.bind((LOCAL_HOST, CLIENT_TCP_PORT))
    client_server_socket.connect((SERVER_HOST, SERVER_PORT))
    server_conn = threading.Thread(target=tcp_message)  # Cria uma thread para a conexao com o servidor gerenciador
    server_conn.start()

    # Criacao e conexao do soquete de comunicacao com o streaming
    client_streaming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_streaming_socket.bind((LOCAL_HOST, CLIENT_UDP_PORT))
    streaming_conn = threading.Thread(target=udp_message)  # Cria uma thread para a conexao com o servidor de streaming
    streaming_conn.start()

    # login do usuario
    username = input("digite o usuario:")
    message = f'ENTRAR_NA_APP {username} {socket.gethostname()}'
    client_server_socket.sendall(message.encode())
    print(f"{message} enviada para o servidor de gerenciamento")

    while True:
        action = input("digite 1 para ver um video, 2 para adicionar um video ou 0 para sair: ")
        if action == 1:
            video_name = input("digite o nome do video que deseja assistir: ")
            quality = input("digite a qualidade do video: ")
            client_streaming_socket.sendto(f'REPRODUZIR_VIDEO {username} {video_name} {quality}'.encode(),
                                           (STREAM_HOST, STREAM_PORT))
        elif action == 0:
            client_server_socket.sendall('SAIR_DA_APP'.encode())
            break
        elif action == 2:
            video_path = input("digite o caminho onde o video esta: ")
            upload_video(video_path)
