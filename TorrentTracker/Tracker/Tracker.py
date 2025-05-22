from flask import Flask, request, jsonify
# built-in libraries
from threading import Thread, Timer
from collections import defaultdict
import json
import datetime
import time
import warnings
warnings.filterwarnings("ignore")

# implemented classes
from utils import *
from configs import CFG, Config

config = Config.from_json(CFG)
next_call = time.time()

app = Flask(__name__)

# In-memory storage for file owners and request frequencies
file_owners_list = defaultdict(list)
send_freq_list = defaultdict(int)
has_informed_tracker = defaultdict(bool)




def save_db_as_json():
    if not os.path.exists(config.directory.tracker_db_dir):
        os.makedirs(config.directory.tracker_db_dir)

    nodes_info_path = config.directory.tracker_db_dir + "nodes.json"
    files_info_path = config.directory.tracker_db_dir + "files.json"

    # saves nodes' information as a json file
    temp_dict = {}
    for key, value in send_freq_list.items():
        temp_dict['node' + str(key)] = value
    nodes_json = open(nodes_info_path, 'w')
    json.dump(temp_dict, nodes_json, indent=4, sort_keys=True)

    # saves files' information as a json file
    files_json = open(files_info_path, 'w')
    json.dump(file_owners_list, files_json, indent=4, sort_keys=True)


@app.route('/tracker', methods=['POST'])
def handle_node_request():
    """Handle a POST request from a node."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    mode = data.get('mode')

    if mode == config.tracker_requests_mode.OWN:
        return add_file_owner(data)
    elif mode == config.tracker_requests_mode.NEED:
        return search_file(data)
    elif mode == config.tracker_requests_mode.UPDATE:
        return update_db(data)
    elif mode == config.tracker_requests_mode.REGISTER:
        return register_node(data)
    elif mode == config.tracker_requests_mode.EXIT:
        return remove_node(data)
    else:
        return jsonify({"error": "Invalid mode"}), 400


def add_file_owner(msg):
    """Add a file owner to the list."""
    entry = {
        'node_id': msg['node_id'],
        'addr': msg['addr']
    }
    log_content = f"Node {msg['node_id']} owns {msg['filename']} and is ready to send."
    log(node_id=0, content=log_content, is_tracker=True)

    file_owners_list[msg['filename']].append(json.dumps(entry))
    file_owners_list[msg['filename']] = list(set(file_owners_list[msg['filename']]))
    send_freq_list[msg['node_id']] += 1
    send_freq_list[msg['node_id']] -= 1

    return jsonify({"status": "File owner added"}), 200


def search_file(msg):
    """Search for a file in the file owner list."""
    log_content = f"Node{msg['node_id']} is searching for {msg['filename']}"
    log(node_id=0, content=log_content, is_tracker=True)

    matched_entries = []
    for json_entry in file_owners_list.get(msg['filename'], []):
        entry = json.loads(json_entry)
        matched_entries.append((entry, send_freq_list[entry['node_id']]))

    # Directly return the response as a dictionary
    response_data = {
        'dest_node_id': msg['node_id'],
        'search_result': matched_entries,
        'filename': msg['filename']
    }

    return jsonify(response_data), 200


def update_db(msg):
    """Update the database with a node's request."""
    send_freq_list[msg["node_id"]] += 1
    save_db_as_json()
    return jsonify({"status": "Database updated"}), 200


def register_node(msg):
    """Register a node as part of the torrent."""
    addr = tuple(msg['addr'])

    has_informed_tracker[(msg['node_id'], addr)] = True
    return jsonify({"status": "Node registered"}), 200


def remove_node(msg):
    """Remove a node from the torrent."""
    node_id = msg['node_id']
    addr = tuple(msg['addr'])
    entry = {
        'node_id': node_id,
        'addr': addr
    }

    try:
        send_freq_list.pop(node_id)
    except KeyError:
        pass

    has_informed_tracker.pop((node_id, addr))
    node_files = file_owners_list.copy()
    # Remove node from file owners list
    for nf in node_files:
        if json.dumps(entry) in file_owners_list[nf]:
            file_owners_list[nf].remove(json.dumps(entry))
        if len(file_owners_list[nf]) == 0:
            file_owners_list.pop(nf)

    save_db_as_json()
    log_content = f"Node {node_id} exited the torrent intentionally."
    log(node_id=0, content=log_content, is_tracker=True)

    return jsonify({"status": "Node removed"}), 200


def check_nodes_periodically(interval: int):
    """Check nodes at periodic intervals."""
    global next_call
    alive_nodes_ids = set()
    dead_nodes_ids = set()

    try:
        for node, has_informed in has_informed_tracker.items():
            node_id, node_addr = node[0], node[1]
            if has_informed:  # it means the node has informed the tracker that is still in the torrent
                has_informed_tracker[node] = False
                alive_nodes_ids.add(node_id)
            else:
                dead_nodes_ids.add(node_id)
                remove_node({'node_id': node_id, 'addr': node_addr})
    except RuntimeError: # the dictionary size maybe changed during iteration, so we check nodes in the next time step
        pass

    if not (len(alive_nodes_ids) == 0 and len(dead_nodes_ids) == 0):
        log_content = f"Node(s) {list(alive_nodes_ids)} is in the torrent and node(s){list(dead_nodes_ids)} have left."
        log(node_id=0, content=log_content, is_tracker=True)

    datetime.now()
    next_call = next_call + interval
    Timer(next_call - time.time(), check_nodes_periodically, args=(interval,)).start()


@app.route('/')
def home():
    return "Tracker is running!"


if __name__ == '__main__':
    log_content = "***************** Tracker program started! *****************"
    log(node_id=0, content=log_content, is_tracker=True)
    t = Thread(target=check_nodes_periodically, args=(config.constants.TRACKER_TIME_INTERVAL,))
    t.daemon = True
    t.start()

    app.run(host='0.0.0.0', port=config.constants.TRACKER_ADDR[1])
