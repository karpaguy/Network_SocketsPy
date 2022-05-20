from http import client
import socket
import select
import errno
import sys

# Endereçando valores, como o HEADERSIZE, o IP e o PORT
HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 5050

# Coletando o nome de usuário.
my_username = input("Username: ")

# AF_INET -> Família IPv4
# SOCK_STREAM -> Usando o protocolo TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#CONNECT
client_socket.connect((IP, PORT))

# Evita o blocking por conta do .recv()
client_socket.setblocking(False)

# Codificando o nome do usuário e coletando seu header.
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')

# Envia para o servidor.
client_socket.send(username_header + username)


# Monta a mensagem do usuário para enviar ao servidor.
# O Try para forçar um loop de receber mensagens de outros usuários.
while True:
  # Cliente coloca a messagem que deseja enviar.
  message = input(f"{my_username} > ")

  # Se tiver qualquer coisa dentro da mensagem, o processo de codificação e coleta do header acontece.
  if message:
    message = message.encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header + message)

  try:
    # Loop para receber mensagem de outros usuários.
    while True:
      username_header = client_socket.recv(HEADER_LENGTH)

      # Se não for recebido nenhum dado, o servidor fecha a conexão.
      if not len(username_header):
        print('Connection closed by the server')
        sys.exit()

      # O header é convertido em int, decodificado e passa pelo .strip().
      username_length = int(username_header.decode('utf-8').strip())

      # Recebe e decodifica o nome do usuário.
      username = client_socket.recv(username_length).decode('utf-8')
    
      # A mensagem passa pelo mesmo processo anterior, entranto aqui não é preciso ver se a mensagem existe, pois passou do user.
      message_header = client_socket.recv(HEADER_LENGTH)
      message_length = int(message_header.decode('utf-8').strip())
      message = client_socket.recv(message_length).decode('utf-8')

      # Mostra a mensagem.
      print(f"{username} > {message}")

# ==== EXCPETIONS
  except IOError as e:
    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
      print('Reading error', str(e))
      sys.exit()
    continue

  except Exception as e:
    print('General error', str(e))
    sys.exit()