import socket
import utils
import threading

utils.init_cache(300)

HOST = '127.0.0.1'  # IP do servidor
SERVER_PORT = 5000  # Porta onde o servidor está escutando
STREAM_HOST = '127.0.0.1'  # IP do servidor de streaming
STREAM_PORT = 5555  # Porta do servidor com o streaming


def logout(user):
    """
    desloga o usuario
    :param user:
    :return 'SAIR_DA_APP_ACK':
    """
    print(user)
    return 'SAIR_DA_APP_ACK'


def get_user_information(user):
    """
    Pega todas as informacoes do usuario e envia para o servidor de streaming
    :param user:
    :return 'USER_INFORMATION' + ' ' + user_id:
    """
    user_tup = utils.get_user_information(user)
    if user_tup is None:
        return 'USER_UNKNOWN'

    name, premium = user_tup
    return f'USER_INFORMATION {name} {bool(premium)}'


def login(user):
    """
    Se achar o usuario no bd, manda a mensagem 'STATUS_DO_USUARIO',
        informando ID, tipo de servico e membros do grupo.
    Caso contrario, cria um no bd e envia 'ENTRAR_NA_APP_ACK' com uma mensagem de confirmacao da criacao.
    :param user:
    :return 'STATUS_DO_USUARIO' + ' ' + user_id || 'ENTRAR_NA_APP_ACK'  :
    """
    print(user)
    user_tup = utils.get_user_information(user)
    if user_tup is None:
        utils.add_user(user)
        return 'ENTRAR_NA_APP_ACK'

    name, premium = user_tup
    return f'STATUS_DO_USUARIO nome:{name} premium?{bool(premium)}'


def threaded_server(host, port):
    while True:
        print("Esperando conexao...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()
        conn, ip = s.accept()
        print('GOT CONNECTION FROM:', ip)
        thread = threading.Thread(target=connection_manager, args=(conn,))
        thread.start()


def connection_manager(conn):
    while conn:
        data_byte = conn.recv(1024)
        data_string = data_byte.decode()
        data = data_string.split(" ")

        if data[0] == 'GET_USER_INFORMATION':
            message = get_user_information(data[1])
        elif data[0] == 'ENTRAR_NA_APP':
            message = login(data[1])
        elif data[0] == 'SAIR_DA_APP':
            message = logout(data[1])

        conn.sendall(message.encode())


def main():
    stream_thread = threading.Thread(target=threaded_server, args=(STREAM_HOST, STREAM_PORT))
    stream_thread.start()
    client_thread = threading.Thread(target=threaded_server, args=(HOST, SERVER_PORT))
    client_thread.start()


if __name__ == "__main__":
    main()
