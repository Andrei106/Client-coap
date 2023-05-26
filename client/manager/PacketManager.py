import logging
import sys

from PySide6.QtCore import Signal, QMutex, QObject

from manager import TokenGenerator
from packet import UDPPacket
from ui import AllFilesEvent, FileEvent

from constants.Constants import MESSAGE_VALID_VERSION, CONFIRMABLE_PACKET_NACK, PACKET_READY, \
    HEADER_MESSAGE_ID_FIELD_KEY, \
    HEADER_TOKEN_FIELD_KEY, HEADER_TYPE_FIELD_KEY, HEADER_PAYLOAD_FIELD_KEY, ALL_FILES, FILE, SAVE_FILE, MOVE_FILE, \
    DELETE_FILE, NEW_FILE, NEW_FOLDER

from client.constants.Constants import HEADER_TYPE_FIELD_KEY, HEADER_CLASS_STATUS_CODE_FIELD_KEY, \
    HEADER_PAYLOAD_FIELD_KEY


class PacketManager(QObject):
    ui_signal = Signal(object)

    def __init__(self, sender, receiver):
        super().__init__()
        self.requests = {}
        self.request_lock = QMutex()  # TODO: use this when altering self.requests
        self.sender = sender
        self.receiver = receiver
        self.receiver.receive_signal.connect(lambda data: self.dispatch(data))
        self.token_generator = TokenGenerator()

    def dispatch(self, data):
        logging.info(f"Attempting to deserialize response {data}")  # TODO: read & validate data
        msg = self.bytes_to_msg(data)
        logging.info(f"Message {msg}")

        # if the received message is an ack then we have to wait until we receive the data,then send an ack
        if msg.header.content[HEADER_TYPE_FIELD_KEY] == 0:
            logging.info("Need ack")
            self.send_ack_msg(msg.header.content[HEADER_MESSAGE_ID_FIELD_KEY])

        if msg.header.content[HEADER_CLASS_STATUS_CODE_FIELD_KEY] == 2:
            logging.info("OK")
            self.request_lock.lock()
            if f"{msg.header.content[HEADER_TOKEN_FIELD_KEY]}" in self.requests and \
                    self.requests[f"{msg.header.content[HEADER_TOKEN_FIELD_KEY]}"][
                        "messageId"] == f"{msg.header.content[HEADER_MESSAGE_ID_FIELD_KEY]}":
                if HEADER_TYPE_FIELD_KEY == 2 and self.requests[f"{msg.header.content[HEADER_TOKEN_FIELD_KEY]}"][
                    "status"] == CONFIRMABLE_PACKET_NACK and (not msg.header.content[HEADER_PAYLOAD_FIELD_KEY] or len(
                        msg.header.content[HEADER_PAYLOAD_FIELD_KEY]) == 0):
                    self.requests[f"{msg.header.content[HEADER_TOKEN_FIELD_KEY]}"]["status"] = PACKET_READY
                else:
                    if self.requests[f"{msg.header.content[HEADER_TOKEN_FIELD_KEY]}"]["expect"] == ALL_FILES:
                        self.ui_signal.emit(AllFilesEvent(msg.header.content[HEADER_PAYLOAD_FIELD_KEY]))
                    if self.requests[f"{msg.header.content[HEADER_TOKEN_FIELD_KEY]}"]["expect"] == FILE:
                        self.ui_signal.emit(FileEvent(msg.header.content[HEADER_PAYLOAD_FIELD_KEY][
                                                      msg.header.content[HEADER_PAYLOAD_FIELD_KEY].index('}') + 1:]))
                    if self.requests[f"{msg.header.content[HEADER_TOKEN_FIELD_KEY]}"]["expect"] in [MOVE_FILE,
                                                                                                    DELETE_FILE,
                                                                                                    NEW_FILE,
                                                                                                    NEW_FOLDER]:
                        self.get_all_files()
                    self.requests[f"{msg.header.content[HEADER_TOKEN_FIELD_KEY]}"] = None

            self.request_lock.unlock()

        if msg.header.content[HEADER_CLASS_STATUS_CODE_FIELD_KEY] == 4:
            logging.info("Server error")
            if msg.header.content[HEADER_PAYLOAD_FIELD_KEY] != "":
                logging.info(msg.header.content[HEADER_PAYLOAD_FIELD_KEY])

        # self.ui_signal.emit(str(data))  # TODO: define ui signals

    def send_confirmable_packet(self, payload, expect):
        message_id = self.token_generator.get_message_id()
        token = self.token_generator.get_token()
        packet = UDPPacket().confirmable_packet(message_id, token,
                                                payload)
        self.sender.send(packet)
        self.request_lock.lock()
        self.requests[token] = {"messageId": message_id, "status": CONFIRMABLE_PACKET_NACK, "expect": expect}
        self.request_lock.unlock()

    def get_all_files(self, CON):

        if CON:
            self.send_confirmable_packet('{"op": "ls", "path": "/"}', ALL_FILES)
        else:
            self.send_non_confirmable_packet('{"op": "ls", "path": "/"}', ALL_FILES)

    def get_file(self, filePath,CON):
        if CON:
            self.send_confirmable_packet('{"op": "cat", "path": "' + filePath.replace("\\", "/") + '"}', FILE)
        else:
            self.send_non_confirmable_packet('{"op": "cat", "path": "' + filePath.replace("\\", "/") + '"}', FILE)

    def new_file(self, filePath,CON):

        if CON:
            self.send_confirmable_packet('{"op": "touch", "path": "' + filePath.replace("\\", "/") + '"}',
                                             NEW_FILE)

        else:
             self.send_non_confirmable_packet('{"op": "touch", "path": "' + filePath.replace("\\", "/") + '"}',
                                              NEW_FILE)

    def new_folder(self, path,CON):
        if CON:
             self.send_confirmable_packet('{"op": "mkdir", "path": "' + path.replace("\\", "/") + '"}', NEW_FILE)
        else:
            self.send_non_confirmable_packet('{"op": "mkdir", "path": "' + path.replace("\\", "/") + '"}', NEW_FILE)

    def move_file(self, fromPath, toPath,CON):
        if (CON):
            self.send_confirmable_packet('{"op": "mv", "path": "' + fromPath.replace("\\\\", "\\").replace("\\",                                                                                               "/") + '", "newPath": "' + toPath.replace(
            "\\", "/") + '"}', MOVE_FILE)
        else:
            self.send_non_confirmable_packet('{"op": "mv", "path": "' + fromPath.replace("\\\\", "\\").replace("\\",
                                                                                                               "/") + '", "newPath": "' + toPath.replace(
                "\\", "/") + '"}', MOVE_FILE)

    def delete_file(self, path,CON):
        if (CON):
           self.send_confirmable_packet('{"op": "rm", "path": "' + path.replace("\\", "/") + '"}', DELETE_FILE)
        else:
            self.send_non_confirmable_packet('{"op": "rm", "path": "' + path.replace("\\", "/") + '"}', DELETE_FILE)

    def send_non_confirmable_packet(self, payload, expect):
        message_id = self.token_generator.get_message_id()
        token = self.token_generator.get_token()
        packet = UDPPacket().non_confirmable_packet(message_id,
                                                    token,
                                                    payload)
        self.sender.send(packet)
        self.request_lock.lock()
        self.requests[token] = {"messageId": message_id, "status": PACKET_READY, "expect": expect}
        self.request_lock.unlock()

    def send_ack_msg(self, message_id):
        packet = UDPPacket().ACK_msg(message_id, self.token_generator.get_token(),
                                     "ack")
        self.sender.send(packet)

    def send_reset(self, message_id):
        packet = UDPPacket().reset(message_id, self.token_generator.get_token())
        self.sender.send(packet)

    def bytes_to_msg(self, data_bytes: bytes):
        # TODO: validate data_bytes + add options
        header_bytes = data_bytes[0:4]
        ver = (header_bytes[0] & 0xC0) >> 6
        type = (header_bytes[0] & 0x30) >> 4
        token_length = (header_bytes[0] & 0x0F)
        msg_class = (header_bytes[1] & 0xE0) >> 5
        msg_detail = (header_bytes[1] & 0x1F)
        msg_id = (header_bytes[2] << 8) + header_bytes[3]

        if ver != MESSAGE_VALID_VERSION:
            logging.info(f"Wrong version detected for message {data_bytes}")
            exit()

        if 9 <= token_length <= 15:
            logging.info(f"Token-length can not be between 9-15")
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
