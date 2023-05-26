import logging
import os
import sys

from PySide6.QtCore import QThreadPool

from manager import CoapPacketSender, CoapPacketReceiver, PacketManager
from ui import DesktopUserInterface

if __name__ == "__main__":
    logging.root.setLevel(logging.NOTSET)
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m-%d-%YT%I:%M:%SZ',
                        level=logging.NOTSET)
    packet_sender = CoapPacketSender()
    packet_receiver = CoapPacketReceiver()
    thread_pool = QThreadPool()
    thread_pool.start(packet_sender)
    thread_pool.start(packet_receiver)
    packet_manager = PacketManager(packet_sender, packet_receiver)
    ui = DesktopUserInterface(sys.argv, os.path.join(os.getcwd(), 'ui/assets/user-interface.ui'), packet_manager)
    sys.exit(ui.start())



