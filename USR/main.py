import socket
import cv2
import pickle
import time
import pyaudio
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
    udp_message()


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
    return


def tcp_message():
    """
    É a função responsável pelo recebimento e processamento de mensagens do servidor de gerenciamento
    :return:
    """
    if client_server_socket:
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
    if client_streaming_socket:
        stream_message = client_streaming_socket.recvfrom(1024)
        print(f"{stream_message[0]} recebida do servidor de streaming")
        data_byte = stream_message[0]
        data_string = data_byte.decode()
        data = data_string.split(' ')
        if data[0] == 'LISTA_DE_VIDEOS':
            video_list(data[1])


def play_video():
    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    start = time.time()
    while True:
        p_frame, _ = client_streaming_socket.recvfrom(1024 * 64)
        if p_frame == b'END_OF_VIDEO':
            break
        c_frame = pickle.loads(p_frame)
        frame = cv2.imdecode(c_frame, 1)
        frame = cv2.putText(frame, 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("REPRODUZINDO VIDEO", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            client_streaming_socket.close()
            break
        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count/(time.time()-st))
                st = time.time()
                cnt = 0
            except:
                pass
        cnt += 1
    print(f"video {time.time() - start}")


def play_audio():
    p = pyaudio.PyAudio()
    # open stream (2)
    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True,
                    frames_per_buffer=1024)
    s_audio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_audio.bind((LOCAL_HOST, CLIENT_UDP_PORT-1))
    start = time.time()
    while True:
        p_audio, _ = s_audio.recvfrom(1024*8)
        if p_audio == b'END_OF_AUDIO':
            break
        audio = pickle.loads(p_audio)
        stream.write(audio)
    print(f"audio {time.time() - start}")


def play_audio_video():
    t_audio = threading.Thread(target=play_audio)
    t_video = threading.Thread(target=play_video)
    t_audio.start()
    t_video.start()


def upload_video(video_name):
    pass


if __name__ == "__main__":
    # Criacao do soquete do servidor
    client_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_server_socket.bind((LOCAL_HOST, CLIENT_TCP_PORT))

    # Criacao do soquete de comunicacao com o streaming
    client_streaming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_streaming_socket.bind((LOCAL_HOST, CLIENT_UDP_PORT))

    # login do usuario
    username = input("digite o usuario:")

    client_server_socket.connect((SERVER_HOST, SERVER_PORT))  # conecta com o servidor de gerenciamento
    message = f'ENTRAR_NA_APP {username} {LOCAL_HOST}'
    client_server_socket.sendall(message.encode())
    tcp_message()
    print(f"{message} enviada para o servidor de gerenciamento")

    while True:
        action = input("digite 1 para ver um video, 2 para adicionar um video ou 0 para sair: ")
        if action == "0":
            client_server_socket.sendall('SAIR_DA_APP'.encode())
            tcp_message()
            break
        elif action == "1":
            video_name = input("digite o nome do video que deseja assistir: ")
            quality = input("digite a qualidade do video: ")
            client_streaming_socket.sendto(f'REPRODUZIR_VIDEO {username} {video_name} {quality}'.encode(),
                                           (STREAM_HOST, STREAM_PORT))
            play_audio_video()
        elif action == "2":
            video_path = input("digite o caminho onde o video esta: ")
            upload_video(video_path)
