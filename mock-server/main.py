import socket
import sys
import select
import threading
import os

#use server.py instead of this !

listen_port = int(os.getenv('LISTEN_PORT', 8080))
peer_address = os.getenv('PEER_ADDRESS', '127.0.0.1')
peer_port = int(os.getenv('PEER_PORT', 8081))

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.bind(('0.0.0.0', listen_port))


def receive():
    global running
    while running:
        r, _, _ = select.select([s], [], [], 1)
        if r:
            data, address = s.recvfrom(1024)
            print(f"Server received {data}")
            s.sendto(bytes("pong", encoding="ascii"), (peer_address, peer_port))


running = True

try:
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
except Exception as ignored:
    sys.exit()

input()
