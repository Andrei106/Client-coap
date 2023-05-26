import logging
import queue
import socket

from PySide6.QtCore import QRunnable


class PacketSender(QRunnable):
    def __init__(self, address="127.0.0.1", port=5683):
        super(PacketSender, self).__init__()
        self.queue = queue.Queue()
        self.is_active = True
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        logging.info('Initialized packet sender')

    def stop(self):
        self.is_active = False
        logging.info('Shutting down packet sender')

    def send(self, packet):
        self.queue.put(packet)

    def run(self) -> None:
        logging.debug(f'Will attempt to send packets to {self.address}:{self.port}')
        while self.is_active:
            try:
                packet = self.queue.get(timeout=1)
                if packet:
                    logging.debug(f'Sending to {self.address}:{self.port} {packet}')
                    self.socket.sendto(packet.serialize(), (self.address, self.port))
            except queue.Empty as ignored:
                pass
