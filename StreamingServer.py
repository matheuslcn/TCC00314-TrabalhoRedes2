import socket


HOST = '127.0.0.1'      # IP do servidor de streaming (localhost)
SERVER_PORT = 5555      # Porta do servidor com o streaming
STREAM_PORT = 6000      # Porta para se comunicar com os clientes

# Cria o soquete para conexao com o servidor e tenta conexao
stream_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Tentando conectar com o servidor...")
stream_server_socket.connect((HOST, SERVER_PORT))
print("Conectado.")

# Cria o soquete para conexao com os clientes e fica escutando
stream_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
stream_client_socket.bind((HOST, STREAM_PORT))
print("Esperando mensagens dos clientes...")

while True:
    data_byte = stream_server_socket.recv(1024)     # Recebe os bytes mandados pelo servidor
    data_string = data_byte.decode()                # Transforma os bytes em uma string
    print(data_string)                              # Mostra a string recebida





