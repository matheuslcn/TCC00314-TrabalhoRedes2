import socket
import utils
import threading

utils.init_cache(300)

HOST = '127.0.0.1'          # IP do servidor
SERVER_PORT = 5000          # Porta onde o servidor está escutando
STREAM_HOST = '127.0.0.1'   # IP do servidor de streaming
STREAM_PORT = 5555          # Porta do servidor com o streaming


def logout():
    """
    desloga o usuario
    :param user:
    :return 'SAIR_DA_APP_ACK':
    """
    return 'SAIR_DA_APP_ACK'


def get_user_information(user):
    """
    Pega todas as informacoes do usuario e envia para o servidor de streaming
    :param user:
    :return 'USER_INFORMATION {user} {boll(premium)}':
    """
    user_tup = utils.get_user_information(user)
    if not user_tup:
        return 'USER_UNKNOWN'

    name, premium = user_tup
    return f'USER_INFORMATION {name} {bool(premium)}'


def login(user):
    """
    Se achar o usuario no bd, manda a mensagem 'STATUS_DO_USUARIO',
        informando ID, tipo de servico e membros do grupo.
    Caso contrario, cria um no bd e envia 'ENTRAR_NA_APP_ACK' com uma mensagem de confirmacao da criacao.
    :param user:
    :return 'STATUS_DO_USUARIO {user} {bool(premium)}' ou 'ENTRAR_NA_APP_ACK'  :
    """
    print(user)
    user_tup = utils.get_user_information(user)
    if not user_tup:
        utils.add_user(user)
        return 'ENTRAR_NA_APP_ACK'

    name, premium = user_tup
    return f'STATUS_DO_USUARIO {name} {bool(premium)}'


def create_connection(host, port):
    """
    Cria um socket TCP e espera conexoes com clientes, quando uma conexao é aceita,
    cria uma thread para o cliente para troca de mensagens
    :param host:
    :param port:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    while True:
        print("Esperando conexao...")
        conn, ip = s.accept()
        print('GOT CONNECTION FROM:', ip)
        thread = threading.Thread(target=threaded_client, args=(conn,))
        thread.start()


def threaded_client(conn):
    """
    Espera receber uma mensagem do cliente e chama uma funcao diferente para cada tipo de mensagem
    :param conn:
    :return:
    """
    while conn:
        data_byte = conn.recv(1024)
        print(f"{data_byte} recebido de um cliente")
        data_string = data_byte.decode()
        data = data_string.split(" ")

        if data[0] == 'GET_USER_INFORMATION':
            message = get_user_information(data[1])
        elif data[0] == 'ENTRAR_NA_APP':
            message = login(data[1])
        elif data[0] == 'SAIR_DA_APP':
            message = logout()
            conn.sendall(message.encode())
            print(f"{message} enviada para um cliente")
            conn.close()
            break
        else:
            print("Mensagem invalida")
            continue
        conn.sendall(message.encode())
        print(f"{message} enviada para um cliente")


def main():
    """
    cria duas threads, uma para a conexao com o servidor de streaming
    e outra para a conexao com os clientes
    :return:
    """
    stream_thread = threading.Thread(target=create_connection, args=(STREAM_HOST, STREAM_PORT))
    stream_thread.start()
    client_thread = threading.Thread(target=create_connection, args=(HOST, SERVER_PORT))
    client_thread.start()


if __name__ == "__main__":
    main()
