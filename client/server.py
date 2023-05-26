import json
import logging
import socket
import sys
import select
import threading
import os

from client.constants.Constants import MESSAGE_VALID_VERSION, HEADER_CLASS_STATUS_CODE_FIELD_KEY, \
    HEADER_DETAIL_STATUS_CODE_FIELD_KEY, HEADER_VER_FIELD_KEY, HEADER_TOKEN_LENGTH_FIELD_KEY, \
    HEADER_TOKEN_FIELD_KEY, HEADER_TYPE_FIELD_KEY, HEADER_MESSAGE_ID_FIELD_KEY, HEADER_PAYLOAD_FIELD_KEY
from client.packet import UDPPacket


def bytes_to_msg(data_bytes: bytes):

    header_bytes = data_bytes[0:4]
    ver = (header_bytes[0] & 0xC0) >> 6
    type = (header_bytes[0] & 0x30) >> 4
    token_length = (header_bytes[0] & 0x0F)
    msg_class = (header_bytes[1] & 0xE0) >> 5
    msg_detail = (header_bytes[1] & 0x1F)
    msg_id = (header_bytes[2] << 8) + header_bytes[3]

    if ver != MESSAGE_VALID_VERSION:
        logging.info(f'Wrong version detected for message {data_bytes}')
        exit()

    if 9 <= token_length <= 15:
        logging.info(f'Token-length can not be between 9-15')
        exit()

    token = 0x0
    if token_length:
        token = int.from_bytes(data_bytes[4:4 + token_length], sys.byteorder)
    payload = data_bytes[4 + token_length + 1:].decode()

    udp_packet = UDPPacket()
    udp_packet.header \
        .ver(str(ver)) \
        .type(type) \
        .token_length(token_length) \
        .token(token) \
        .class_status_code(msg_class) \
        .detail_status_code(msg_detail) \
        .message_id(msg_id) \
        .payload(payload)
    return udp_packet


listen_port = int(os.getenv('LISTEN_PORT', 5683))
peer_address = os.getenv('PEER_ADDRESS', '127.0.0.1')
peer_port = int(os.getenv('PEER_PORT', 5684))

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.bind(('0.0.0.0', listen_port))


def receive():
    global running
    while running:
        r, _, _ = select.select([s], [], [], 1)
        if r:
            data, address = s.recvfrom(1024)
            print(f"Server received {data}")
            packet = bytes_to_msg(data)
            print(packet)
            if (str(packet.header.content[HEADER_CLASS_STATUS_CODE_FIELD_KEY]) + "." +str(packet.header.content[HEADER_DETAIL_STATUS_CODE_FIELD_KEY])) == "0.0":
                payload = json.loads(packet.header.content[HEADER_PAYLOAD_FIELD_KEY])
                if payload['op'] == 'ls':
                    f = open("files_struct.json", "r")
                    udp_packet = UDPPacket()
                    udp_packet.header \
                        .ver(str(packet.header.content[HEADER_VER_FIELD_KEY])) \
                        .type(packet.header.content[HEADER_TYPE_FIELD_KEY]) \
                        .token_length(packet.header.content[HEADER_TOKEN_LENGTH_FIELD_KEY]) \
                        .token(packet.header.content[HEADER_TOKEN_FIELD_KEY]) \
                        .class_status_code(2) \
                        .detail_status_code(0) \
                        .message_id(packet.header.content[HEADER_MESSAGE_ID_FIELD_KEY]) \
                        .payload(f.read())
                    s.sendto(udp_packet.serialize(), (peer_address, peer_port))
                elif payload['op'] == 'cat':
                    f = open("file.txt", "rb")
                    udp_packet = UDPPacket()
                    udp_packet.header \
                        .ver(str(packet.header.content[HEADER_VER_FIELD_KEY])) \
                        .type(packet.header.content[HEADER_TYPE_FIELD_KEY]) \
                        .token_length(packet.header.content[HEADER_TOKEN_LENGTH_FIELD_KEY]) \
                        .token(packet.header.content[HEADER_TOKEN_FIELD_KEY]) \
                        .class_status_code(2) \
                        .detail_status_code(0) \
                        .message_id(packet.header.content[HEADER_MESSAGE_ID_FIELD_KEY]) \
                        .payload('{"idx": 1, "total": 1}')
                    udp_packet.body = f.read()
                    s.sendto(udp_packet.serialize(), (peer_address, peer_port))

         #  s.sendto(bytes("pong", encoding="ascii"), (peer_address, peer_port))


running = True

try:
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
except Exception as ignored:
    sys.exit()

input()
