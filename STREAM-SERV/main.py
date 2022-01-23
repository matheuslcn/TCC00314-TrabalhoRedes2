import socket
import pickle
import cv2
import imutils
import wave
import pyaudio
import threading
import time
import utils

HOST = '127.0.0.1'  # IP do servidor de streaming (localhost)
SERVER_PORT = 5555  # Porta do servidor com o streaming
STREAM_PORT = 6000  # Porta para se comunicar com os clientes


def list_videos():
    """
    pega a lista dos videos disponiveis e retorna uma string com LISTA_DE_VIDEOS
    e uma lista com os nomes dos videos
    :returnf'LISTA_DE_VIDEOS lista_dos_videos_para_reproducao':
    """
    return f'LISTA_DE_VIDEOS lista_dos_videos_para_reproducao'


def get_user_information(user):
    """
    prepara uma mensagem para pedir as informacoes do usuario para o servidor de gerenciamento
    :param user:
    :return:
    """
    return f'GET_USER_INFORMATION {user}'


def send_video(video, client_addr):
    cap = cv2.VideoCapture(video)
    fps = (cap.get(cv2.CAP_PROP_FPS))
    print(f"video fr {fps}")
    while cap.isOpened():
        begin = time.time()
        ret, frame = cap.read()

        if not ret:
            print("Can't receive more frames.")
            break

        _, buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        pframe = pickle.dumps(buffer)
        stream_client_socket.sendto(pframe, (client_addr[0], client_addr[1] + 1))

        diff_time = time.time() - begin
        if diff_time < 1 / fps:
            time.sleep((1 / fps) - diff_time)

    stream_client_socket.sendto(b'END_OF_VIDEO', (client_addr[0], client_addr[1] + 1))
    cap.release()
    cv2.destroyAllWindows()


def send_audio(audio, client):
    print(audio)
    wf = wave.open(audio, 'rb')
    print(f"audio fr {wf.getframerate()}")
    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    frames_per_buffer=1024)

    # read data
    data = wf.readframes(1024)
    while len(data) > 0:
        p_data = pickle.dumps(data)
        stream_client_socket.sendto(p_data, (client[0], client[1] + 2))
        stream.write(data)
        data = wf.readframes(1024)
    stream_client_socket.sendto(b'END_OF_AUDIO', (client[0], client[1] + 2))
    # stop stream (4)
    stream.close()

    # close PyAudio (5)
    p.terminate()


def send_audio_video(client_addr, video_name, quality):
    video_path = f"STREAM-SERV/video_fls/{video_name}/{quality}.mp4"
    audio_path = f"STREAM-SERV/video_fls/{video_name}/audio.wav"
    video_thread = threading.Thread(target=send_video, args=(video_path, client_addr))
    audio_thread = threading.Thread(target=send_audio, args=(audio_path, client_addr))
    video_thread.start()
    audio_thread.start()


def send_audio_video_one_person(client_addr, video_name, quality, is_premium):
    if not is_premium:
        """
        Deve transmitir o video e mostrar a mensagem:
        “REPRODUZINDO O VÍDEO <<NOME DO VÍDEO>>, COM RESOLUÇÃO <<NOMENCLATURA DA RESOLUÇÃO>>”.
        """
        send_audio_video(client_addr, video_name, quality)

    else:
        """
         Deve mostrar a mensagem:
        "NÃO TEM PERMISSÃO PARA REPRODUZIR VÍDEOS, POR FAVOR MUDE SUA CLASSIFICAÇÃO."
        """
    return


def send_audio_video_group(group, video_name, quality, isPremium):
    if isPremium:
        for user in group:
            thread = threading.Thread(target=send_audio_video, args=(user, video_name, quality))
            thread.start()
    else:
        """
         Deve mostrar a mensagem:
        "NÃO TEM PERMISSÃO PARA REPRODUZIR VÍDEOS, POR FAVOR MUDE SUA CLASSIFICAÇÃO."
        """


def stop_streaming(user_ip):
    """
    deve parar o streaming para o usuario
    :param user_ip:
    :return:
    """
    return


def stop_group_streaming(user_ip):
    """
    deve parar o streaming para o grupo
    :param user_ip:
    :return:
    """
    return


def server_connection(message):
    """
    É a funcao responsável por enviar e receber mensagens do servidor de gerenciamento.
    :param message:
    :return:
    """
    stream_server_socket.sendall(message.encode())
    data_byte = stream_server_socket.recv(1024)
    data_string = data_byte.decode()
    data = data_string.split(' ')
    if data[0] == 'USER_INFORMATION':
        return data[2]


def threaded_client(message):
    """
    É a funcao que processa a mensagem recebida pelo cliente, e de acordo com o tipo de mensagem,
    chama uma, ou mais, funcoes diferentes
    :param message:
    :return:
    """
    data_byte = message[0]
    data_string = data_byte.decode()
    data = data_string.split(' ')
    client_addr = message[1]

    if data[0] == 'LISTAR_VIDEOS':
        message = list_videos()
        stream_client_socket.sendto(message.encode(), client_addr)
    elif data[0] == 'REPRODUZIR_VIDEO':
        message_to_server = get_user_information(data[1])
        is_premium= server_connection(message_to_server)
        send_audio_video_one_person(client_addr, data[2], data[3], is_premium)
    elif data[0] == 'PLAY_VIDEO_TO_GROUP':
        message_to_server = get_user_information(data[1])
        is_premium, group_members = server_connection(message_to_server)
        send_audio_video_group(group_members, data[2], data[3], is_premium)
    elif data[0] == 'PARAR_STREAMING':
        stop_streaming(client_addr)
    else:
        print("Mensagem invalida")


def client_connection():
    """
    É a funcao que recebe a mensagem de um cliente e cria uma thread para o seu processamento.
    :return:
    """
    while stream_client_socket:
        client_message = stream_client_socket.recvfrom(1024)
        client_thread = threading.Thread(target=threaded_client, args=(client_message,))
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
