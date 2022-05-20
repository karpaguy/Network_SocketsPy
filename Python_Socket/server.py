import socket
import threading

HEADER = 64
PORT = 5050 # Verificar o porquê de um port ser 5050, o que fazem também. - Esse port não é usado no computador, então serve.
# SERVER = "meu ip fica aqui"
SERVER = socket.gethostbyname(socket.gethostname()) #Ip address
ADDR = (SERVER, PORT) # Para fazer o bind do servidor, o address deve estar em uma tuple.
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'

# Socket para abrir este dispositivo a outros
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Diz qual tipo de conexão estamos atrás | Streaming data
server.bind(ADDR) # O servidor foi 'ligado' a esse address, o que significa que qualquer conexão virá a esse soquete.

def handle_client(conn, addr): # Handle the individual connection between the client and server.
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT) # Blocking line code.
        if msg_length: # Se a primeira mensagem for zerada, não roda o código. No caso a 1° '''mensagem''' sempre será zerada,
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f'[{addr}] {msg}')
            conn.send('Msg received'.encode(FORMAT))

    conn.close()

def start(): # Handle new connections and distributte these.
    server.listen()
    print(f"[LISTENING] Server in listening on {SERVER}")
    while True:
        conn, addr = server.accept() 
# O código vai esperar aqui até uma nova conexão. Quando acontece, é armazenado o address da conexão e depois faremos um objeto
# - com isso para enviar informação de volta: 'conn'. - Blocking line code.
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        # How many threads are actives, threads = clients, except the start() thread.

print("[STARTING] server is starting...")
start()