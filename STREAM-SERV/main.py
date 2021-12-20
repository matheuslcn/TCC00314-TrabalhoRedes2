import socket
import threading

HOST = '127.0.0.1'  # IP do servidor de streaming (localhost)
SERVER_PORT = 5555  # Porta do servidor com o streaming
STREAM_PORT = 6000  # Porta para se comunicar com os clientes


def list_videos():
    return f'LISTA_DE_VIDEOS lista_dos_videos_para_reproducao'


def get_user_information(user):
    return f'GET_USER_INFORMATION {user}'


def play_video(user_ip, video, quality, is_premium):
    if is_premium:
        """
        Deve transmitir o video e mostrar a mensagem:
        “REPRODUZINDO O VÍDEO <<NOME DO VÍDEO>>, COM RESOLUÇÃO <<NOMENCLATURA DA RESOLUÇÃO>>”.
        """
        return
    else:
        """
        Deve mostrar a mensagem:
        "NÃO TEM PERMISSÃO PARA REPRODUZIR VÍDEOS, POR FAVOR MUDE SUA CLASSIFICAÇÃO".
        """
        return


def stop_streaming(user_ip):
    """
    deve parar o streaming do usuario
    :param user:
    :return:
    """
    return


def server_connection(message):
    stream_server_socket.sendall(message.encode())
    data_byte = stream_server_socket.recv(1024)
    data_string = data_byte.decode()
    data = data_string.split(' ')
    if data[0] == 'USER_INFORMATION':
        return data[2]


def threaded_client(message):
    data_byte = message[0]
    data_string = data_byte.decode()
    data = data_string.split(' ')
    client_addr = message[1]

    if data[0] == 'LISTAR_VIDEOS':
        message = list_videos()
        print(f"mandando a lista de videos para o {client_addr}")
        stream_client_socket.sendto(message.encode(), client_addr)
        print("lista enviada")
    if data[0] == 'REPRODUZIR_VIDEO':
        message_to_server = get_user_information(data[1])
        is_premium = server_connection(message_to_server)
        play_video(client_addr, data[2], data[3], is_premium)
    if data[0] == 'PARAR_STREAMING':
        stop_streaming(client_addr)
    return


def client_connection():
    while True:
        client_message = stream_client_socket.recvfrom(1024)
        client_thread = threading.Thread(target=threaded_client, args=(client_message, ))
        client_thread.start()


if __name__ == "__main__":
    # Cria o soquete para conexao com o servidor e tenta conexao
    stream_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Tentando conectar com o servidor...")
    stream_server_socket.connect((HOST, SERVER_PORT))
    print("Conectado.")

    # Cria o soquete para conexao com os clientes e fica escutando
    stream_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    stream_client_socket.bind((HOST, STREAM_PORT))
    print("Esperando mensagens dos clientes...")
    client_connection()
