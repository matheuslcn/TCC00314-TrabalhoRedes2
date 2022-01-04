import socket
import threading
import utils
import cv2
import imutils
import pickle
import pyaudio
import time
import wave
import moviepy.editor as mp

HOST = '127.0.0.1'  # IP do servidor de streaming (localhost)
SERVER_PORT = 5555  # Porta do servidor com o streaming
STREAM_PORT = 6000  # Porta para se comunicar com os clientes


def list_videos():
    """
    pega a lista dos videos disponiveis e retorna uma string com LISTA_DE_VIDEOS
    e uma lista com os nomes dos videos
    :returnf'LISTA_DE_VIDEOS lista_dos_videos_para_reproducao':
    """
    videos = utils.list_all_videos()
    return f'LISTA_DE_VIDEOS {videos}'


def get_user_information(user):
    """
    prepara uma mensagem para pedir as informacoes do usuario para o servidor de gerenciamento
    :param user:
    :return:
    """
    return f'GET_USER_INFORMATION {user}'


def send_video(video_name, client_addr):
    cap = cv2.VideoCapture(video_name)
    fps = (cap.get(cv2.CAP_PROP_FPS))
    print(f"video fr {fps}")
    while cap.isOpened():
        begin = time.time()
        ret, frame = cap.read()

        if not ret:
            print("Can't receive more frames.")
            break

        frame = imutils.resize(frame, width=720)
        _, buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        pframe = pickle.dumps(buffer)
        stream_client_socket.sendto(pframe, client_addr)

        diff_time = time.time() - begin
        if diff_time < 0.5/fps:
            time.sleep((0.5/fps) - diff_time)

    stream_client_socket.sendto(b'END_OF_VIDEO', client_addr)
    cap.release()
    cv2.destroyAllWindows()


def send_audio(audio, client):
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
        stream_client_socket.sendto(p_data, (client[0], client[1]-1))
        stream.write(data)
        data = wf.readframes(1024)
    stream_client_socket.sendto(b'END_OF_AUDIO', (client[0], client[1]-1))
    # stop stream (4)
    stream.close()

    # close PyAudio (5)
    p.terminate()


def send_audio_video(client_addr, video_name, quality, is_premium):
    if is_premium:
        """
        Deve transmitir o video e mostrar a mensagem:
        “REPRODUZINDO O VÍDEO <<NOME DO VÍDEO>>, COM RESOLUÇÃO <<NOMENCLATURA DA RESOLUÇÃO>>”.
        """
        video_path = f'video_fls/{video_name}/{quality}.mp4'
        audio_path = f'video_fls/{video_name}/audio.wav'
        video_thread = threading.Thread(target=send_video, args=(video_path, client_addr))
        audio_thread = threading.Thread(target=send_audio, args=(audio_path, client_addr))
        video_thread.start()
        audio_thread.start()

    else:
        """
         Deve mostrar a mensagem:
        "NÃO TEM PERMISSÃO PARA REPRODUZIR VÍDEOS, POR FAVOR MUDE SUA CLASSIFICAÇÃO."
        """
    return


def stop_streaming(user_ip):
    """
    deve parar o streaming do usuario
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
    print(f"{message} enviado para o servidor de gerenciamento")
    data_byte = stream_server_socket.recv(1024)
    print(f"{data_byte} recebido do servidor de gerenciamento")
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
        print(f"{message} enviado para o cliente {client_addr}")
    elif data[0] == 'REPRODUZIR_VIDEO':
        message_to_server = get_user_information(data[1])
        is_premium = server_connection(message_to_server)
        send_video(client_addr, data[2], data[3], is_premium)
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
        print(f"{client_message[0]} recebida do cliente {client_message[1]}")
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
