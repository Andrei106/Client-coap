import logging
import select
import socket

from PySide6.QtCore import QRunnable, Signal, QObject

from constants.Constants import PACKET_MAX_SIZE


class PacketReceiver(QRunnable, QObject):
    receive_signal = Signal(object)

    def __init__(self, interface='0.0.0.0', port=5684):
        QObject.__init__(self)
        QRunnable.__init__(self)
        self.port = port
        self.interface = interface
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.bind((self.interface, self.port))
        self.is_active = True
        logging.info('Initialized packet receiver')

    def stop(self):
        self.is_active = False
        logging.info('Shutting down packet receiver')

    def run(self) -> None:
        logging.debug(f'Listening on {self.interface}:{self.port}')
        while self.is_active:
            response, _, _ = select.select([self.socket], [], [], 1)
            if response:
                data, address = self.socket.recvfrom(PACKET_MAX_SIZE)
                logging.debug(f'Received {len(data)} bytes from {address}')
                self.receive_signal.emit(data)
