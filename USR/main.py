import socket

LOCAL_HOST  = '127.0.0.1'   # localhost
SERVER_HOST = '127.0.0.1'   # IP do servidor
STREAM_HOST = '127.0.0.1'   # IP do stream
CLIENT_PORT = 6060          # Porta do cliente
SERVER_PORT = 5000          # Porta usada pelo servidor
STREAM_PORT = 5050          # Porta onde o cliente vai se comunicar com o servidor de streaming

# Criacao e conexao do soquete do servidor
client_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_server_socket.bind((LOCAL_HOST, CLIENT_PORT))
client_server_socket.connect((STREAM_HOST, SERVER_PORT))

# Criacao do soquete de comunicacao com o streaming
client_streaming_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    pass








