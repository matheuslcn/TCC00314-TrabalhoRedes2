import socket

HOST = '127.0.0.1'          # IP do servidor
SERVER_PORT = 5000          # Porta onde o servidor está escutando
STREAM_HOST = '127.0.0.1'   # IP do servidor de streaming
STREAM_PORT = 5555          # Porta do servidor com o streaming

# Cria o soquete do servidor com o streaming e comeca a ouvir
server_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_stream_socket.bind((HOST, STREAM_PORT))
server_stream_socket.listen()
print("Esperando conexão o Streaming...")

# Aceita a conexao com o streaming
stream_connection, stream_ip = server_stream_socket.accept()
print('GOT CONNECTION FROM:', stream_ip)

# Cria o soquete para os clientes e comeca a ouvir
server_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_client_socket.bind((HOST, SERVER_PORT))
server_client_socket.listen()
print('Esperando conexão do cliente...')

# Aceita uma conexao com o cliente
while True:
    client_connection, client_ip = server_client_socket.accept()
    print('GOT CONNECTION FROM:', client_ip)





