import socket
import pickle

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 5050))


while True:
  full_msg = b''
  new_msg = True
  while True:
    msg = s.recv(16)
    if new_msg:
      # Message length, the size, for example: 22
       print(f'New message length: {msg[:HEADERSIZE]}')
       msglen = int(msg[:HEADERSIZE])
       new_msg = False

    print(f"full message length: {msglen}")

    full_msg += msg

    print(len(full_msg))

    if len(full_msg)-HEADERSIZE==msglen:
      print('Full msg recvd')
      print(full_msg[HEADERSIZE:])

      d = pickle.loads(full_msg[HEADERSIZE:])
      print(d)

      new_msg = True
      full_msg = b''