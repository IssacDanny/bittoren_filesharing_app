import socket
import random
import warnings
import os
import bencodepy
import hashlib
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

def free_socket(sock: socket.socket):
    '''
    This function free a socket to be able to be used by others

    :param sock: socket
    :return:
    '''
    used_ports.remove(sock.getsockname()[1])
    sock.close()

def generate_random_port() -> int:
    '''
    This function generates a new(unused) random port number

    :return: a random integer in range of [1024, 65535]
    '''
    available_ports = config.constants.AVAILABLE_PORTS_RANGE
    rand_port = random.randint(available_ports[0], available_ports[1])
    while rand_port in used_ports:
        rand_port = random.randint(available_ports[0], available_ports[1])

    return rand_port

def parse_command(command: str):
    '''
    This function parses the input command

    :param command: A string which is the input command.
    :return: Command parts (mode, filename)
    '''
    parts = command.split(' ')
    try:
        if len(parts) == 4:
            mode = parts[2]
            filename = parts[3]
            return mode, filename
        elif len(parts) == 3:
            mode = parts[2]
            filename = ""
            return mode, filename
    except IndexError:
        warnings.warn("INVALID COMMAND ENTERED. TRY ANOTHER!")
        return

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

def calculate_file_hash(file_path):
    """ Calculate the SHA1 hash of the specified file. """
    hasher = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.digest()


def create_torrent(file_path, output_path):
    """ Create a torrent file for the specified file. """
    # Ensure the file exists
    if not os.path.isfile(file_path):
        print(f"File '{file_path}' does not exist.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Prepare the torrent metadata
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_hash = calculate_file_hash(file_path)
    tracker_url = f"http://{config.constants.TRACKER_ADDR[0]}:{config.constants.TRACKER_ADDR[1]}/tracker"

    torrent_data = {
        b'info': {
            b'piece length': 9216,  # 16 KB
            b'pieces': file_hash,  # The hash of the file
            b'name': file_name.encode(),
            b'total length': file_size,
        },
        b'announce': tracker_url.encode(),  # Example tracker URL
    }

    # Define the output torrent file path
    torrent_file_path = os.path.join(output_path, f"{file_hash.hex()}.torrent")

    # Bencode the data and write to a file
    with open(torrent_file_path, 'wb') as f:
        f.write(bencodepy.encode(torrent_data))


def parse_torrent_file(torrent_file_path):
    """ Parse and return the contents of a torrent file as a list. """
    if not os.path.isfile(torrent_file_path):
        print(f"Torrent file '{torrent_file_path}' does not exist.")
        return []

    # Read the torrent file
    with open(torrent_file_path, 'rb') as f:
        torrent_data = bencodepy.decode(f.read())

    # Extract relevant information
    info = torrent_data.get(b'info', {})
    parsed_info = [
        torrent_data.get(b'announce').decode(),  # Tracker URL
        info.get(b'name').decode(),  # Name
    ]

    return parsed_info

