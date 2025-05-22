import socket
import random
import warnings
import os
from datetime import datetime
from configs import CFG, Config
config = Config.from_json(CFG)

# global variables
used_ports = []

def set_socket(port: int) -> socket.socket:
    '''
    This function creates a new UDP socket

    :param port: port number
    :return: A socket object with an unused port number
    '''
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', port))
    used_ports.append(port)

    return sock


def log(node_id: int, content: str, is_tracker=False) -> None:
    '''
    This function is used for logging

    :param node_id: Since each node has an individual log file to be written in
    :param content: content to be written
    :return:
    '''
    if not os.path.exists(config.directory.logs_dir):
        os.makedirs(config.directory.logs_dir)

    # time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    content = f"[{current_time}]  {content}\n"
    print(content)

    if is_tracker:
        node_logs_filename = config.directory.logs_dir + '_tracker.log'
    else:
        node_logs_filename = config.directory.logs_dir + 'node' + str(node_id) + '.log'
    if not os.path.exists(node_logs_filename):
        with open(node_logs_filename, 'w') as f:
            f.write(content)
            f.close()
    else:
        with open(node_logs_filename, 'a') as f:
            f.write(content)
            f.close()




