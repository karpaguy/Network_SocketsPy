from ast import expr_context
from http import client
import socket
import select

from matplotlib.pyplot import close

# Endereçando valores, como o HEADERSIZE, o IP e o PORT
HEADER_LENGHT = 10
IP = '127.0.0.1'
PORT = 5050

# AF_INET -> Família IPv4
# SOCK_STREAM -> Usando o protocolo TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Para impedir o erro de "endereço sendo utilizado".
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind e Listen
server_socket.bind((IP, PORT))
server_socket.listen()

# Lista com todos os soquetes presentes no servidor, será utilizada mais tarde, por enquanto só possui o soquete do server.
sockets_list = [server_socket]

# Lista de clientes conectados - soquete como uma chave/key, header e nome como 'data'
clients = {}

# Função para receber mensagens dentro do servidor, passando o client_socket como argumento.
def receive_message(client_socket):

# Try e Excpet, o Excpet em caso da conexão ser fechada de forma "bruta", seja parando o código com Ctrl + C ou outra razão.
# socket.close() e socket.shutdown(socket.SHUT_RDWR) também fazem isso.

  try:
    # Recebe o header da mensagem antes de tudo.
    message_header = client_socket.recv(HEADER_LENGHT)

    # Se o header estiver vazio por qualquer motivo (talvez tenha apenas apertado enter) quebra esse try.
    if not len(message_header):
      return False

    # Decodifica o tamanho da mensagem através do header - procedimento padrão usando .decode('utf-8).strip()
    message_length = int(message_header.decode('utf-8').strip())

    # Retorna um objeto do 'header' e 'data' da mensagem
    return {'header': message_header, 'data': client_socket.recv(message_length)}

# Except.
  except:
    return False

# Receber conexões ou fazer um broadcast de mensagens.
while True:
  # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
  # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
  # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
  read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

  # Iterate over notified sockets
  for notified_socket in read_sockets:
    # Se o notified_socket for igual ao server_socket, então uma nova conexão é feita.
    if notified_socket == server_socket:
      client_socket, client_address = server_socket.accept()

      # Uma das primeiras coisas que devem ser recebidas é o nome do usuário.
      # O valor é coletado através da função receive_message usando o mesmo argumento client_socket
      user = receive_message(client_socket)

      # Conexão foi cortada antes do cliente colocar seu nome de usuário, mas mesmo assim, queremos continuar.
      if user is False:
        continue

      # Adicionamos a nova conexão a nossa lista de sockets.
      sockets_list.append(client_socket)

      # Além disso salvamos seu nome de usuário e header do nome de usuário.
      # Tudo isso é feito com o client_socket, anexando as informações como user na lista.
      # Sempre se cria um único, devido o [].
      clients[client_socket] = user

      print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")

    # Se o notified_socket não for igual ao do server_scoket, significa que temos que dar broadcast.
    else:
      message = receive_message(notified_socket)

      # Cliente fechou a conexão, e isso foi interpretado pela message, portanto, é preciso deletar as informações do cliente e seguir.
      if message is False:
        print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

        # Remove da lista de sockets
        sockets_list.remove(notified_socket)

        # Remove da lista de usuários
        del clients[notified_socket]

        continue

      # Só pegando o *user* e fazendo toda a sacanagem de printar as informações armazenadas nele.
      user = clients[notified_socket]
      print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

      # Fazendo o broadcast.
      for client_socket in clients:
        # Menos pro próprio cliente.
        if client_socket != notified_socket:
          client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

# ==== EXCPETIONS
  for notified_socket in exception_sockets:
    sockets_list.remove(notified_socket)
    del clients[notified_socket]