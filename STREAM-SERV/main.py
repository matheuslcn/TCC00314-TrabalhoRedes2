import socket
import pickle
import cv2
import wave
import pyaudio
import threading
import time
import utils
import moviepy.editor as mp
import os

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

        _, buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        pframe = pickle.dumps(buffer)
        stream_client_socket.sendto(pframe, (client_addr[0], client_addr[1] + 1))

        diff_time = time.time() - begin
        if diff_time < 1/fps:
            time.sleep((1/fps) - diff_time)

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
    if is_premium:
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
        g = group.split(',')
        for user in g:
            if user:
                message_to_server = get_user_information(user)
                user_ip, _, _ = server_connection(message_to_server)
                thread = threading.Thread(target=send_audio_video, args=(user_ip, video_name, quality))
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


def extract_audio(video):
    my_clip = mp.VideoFileClip(f"STREAM-SERV/video_fls/{video}/temp.mp4")
    my_clip.audio.write_audiofile(f"STREAM-SERV/video_fls/{video}/audio.wav")
    my_clip.close()


def convert_video(video_name):
    cap = cv2.VideoCapture(f'STREAM-SERV/video_fls/{video_name}/temp.mp4')
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out_240 = cv2.VideoWriter(f'STREAM-SERV/video_fls/{video_name}/240.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), (426, 240))
    out_480 = cv2.VideoWriter(f'STREAM-SERV/video_fls/{video_name}/480.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), (854, 480))
    out_720 = cv2.VideoWriter(f'STREAM-SERV/video_fls/{video_name}/720.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), (1280, 720))
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame_240 = cv2.resize(frame, (426, 240), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
            frame_480 = cv2.resize(frame, (854, 480), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
            frame_720 = cv2.resize(frame, (1280, 720), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
            out_240.write(frame_240)
            out_480.write(frame_480)
            out_720.write(frame_720)
        else:
            break

    cap.release()
    out_240.release()
    out_480.release()
    out_720.release()
    cv2.destroyAllWindows()


def video_download(client_addr, video_name, video_path):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, STREAM_PORT - 1))
    try:
        os.mkdir(f'STREAM-SERV/video_fls/{video_name}')
    except FileExistsError:
        count = 2
        while True:
            video_name_temp = video_name + f'({count})'
            try:
                os.mkdir(f'STREAM-SERV/video_fls/{video_name_temp}')
                video_name = video_name_temp
                break
            except FileExistsError:
                count += 1

    v = open(f"STREAM-SERV/video_fls/{video_name}/temp.mp4", 'wb')
    s.sendto(f'UPLOAD_ACK {video_path}'.encode(), client_addr)
    while True:
        msg, _ = s.recvfrom(1024)
        if msg == b'END_OF_FILE':
            break
        v.write(msg)
    v.close()

    extract_audio(video_name)
    print("Convertendo os videos...")
    convert_video(video_name)
    os.remove(f"STREAM-SERV/video_fls/{video_name}/temp.mp4")
    print("Video salvo")


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
        return data[2], eval(data[3]), data[4]


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
        _, is_premium, _ = server_connection(message_to_server)
        send_audio_video_one_person(client_addr, data[2], data[3], is_premium)
    elif data[0] == 'PLAY_VIDEO_TO_GROUP':
        message_to_server = get_user_information(data[1])
        _, is_premium, group_members = server_connection(message_to_server)
        send_audio_video_group(group_members, data[2], data[3], is_premium)
    elif data[0] == 'UPLOAD':
        t = threading.Thread(target=video_download, args=(client_addr, data[1], data[2]))
        t.start()
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
