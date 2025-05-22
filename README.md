# I. Introduction

BitTorrent is a widely-used peer-to-peer (P2P) protocol designed for the efficient
distribution of large files across networks. In this decentralized system, the collective
group of peers involved in the sharing of a specific file is referred to as a "torrent."
Each peer in a torrent participates by downloading and uploading equally sized
chunks of the file, facilitating collaborative file distribution. Upon initially joining a
torrent, a peer begins without any file chunks and gradually accumulates them over
time as it interacts with other peers. Concurrently, while it downloads chunks, it also
contributes by uploading chunks to assist other peers.

At the core of each torrent lies an infrastructure node known as a tracker. The
tracker plays a crucial role in managing the torrent’s ecosystem, helping peers
discover and maintain connections with one another. When a peer joins a torrent, it
registers with the tracker, which then monitors its status and participation.
Periodically, the peer informs the tracker of its continued involvement, ensuring that
the tracker remains updated with the current list of active participants in the torrent.
This system helps maintain the decentralized nature of file distribution while ensuring
seamless coordination between peers.

# II. How to run it

BitTorrent operates with two primary modules: (i) the node, also known as the
peer, and (ii) the tracker. Consequently, it is necessary to run each of these modules
separately.

1. tracker.py:

```
Run the script: python3 tracker.py
```

2. TorrentClient.py: You have the flexibility to create as many peers as required.
    For instance, the process of creating two nodes is illustrated below. Please
    note that each node must be executed in a separate terminal window if the
    project is being run on a single local machine.

```
Run the script: python3 TorrentClient.py -node_id 1
```
#In another tab of terminal

```
Run the script: python3 TorrentClient.py -node_id 2
```
As demonstrated, the process requires the input of the node ID that you wish to
create. For the sake of simplicity, it is assumed that each node possesses a unique ID.

# III. Usage

At this stage, the peers are operational within the torrent; however, there remains
much to be done. As outlined in the course project description, each node can operate
in one of two modes, meaning that there are two distinct functionalities for each node:

 Send (Upload): At any given moment, a node 𝑖 may wish to upload a file to a
neighboring peer within the torrent. The process begins with node 𝑖 generating a
torrent file, which includes essential information such as the file name, the tracker
URL, the length of each file piece, the file's hash, and the total file length.
Following this, node 𝑖 notifies the tracker that it possesses the file and is
prepared to enter a state where it awaits requests from other peers for the specific
file. A node can activate this mode by entering the following command:
torrent -setMode send <filename>

 Download: Inorder to download a file,a node must have the torrent file of that
file. When node intends to download a file, it must first read the corresponding
torrent file to retrieve key information such as the file name and the tracker URL.
Subsequently, node notifies the tracker of its request for the file. The tracker then
searches for the file within the torrent and ranks the neighboring peers that
possess the file based on their upload frequency. The higher a node's upload
frequency, the greater its likelihood of being selected. A fixed number of
neighboring peers are then chosen for node 𝑖, who will later request the file from
them. Following this, node 𝑖 sends a request to the selected peers and establishes
a UDP connection to retrieve chunks of the file from those peers.A node can
activate this mode by entering the following command:
torrent -setMode download <Torrentfilename>

 Exit (Optional Mode): An optional mode, referred to as "exit," has been
implemented to inform the tracker when a node intentionally leaves the torrent.
However, according to the reference book, the tracker should automatically detect


when a node has exited. This mechanism is further detailed in the project report.A
node can activate this mode by entering the following command:
torrent -setMode exit

Each node, as well as the tracker, maintains an individual log file located in the logs/
directory. This log file records all events related to the specific node or tracker within
the torrent.

Additionally, any files that a node participates in within the torrent can be placed in
the node's local directory, which can be found under node_files/.

# IV. Configuration

All configurable parameters and settings are located in the configs.py file. Within this
file, there exists a JSON-like variable, structured as follows:

```
{
"directory": {
"logs_dir": "logs/",
"node_files_dir": "node_files/",
"tracker_db_dir": "tracker_db/"
},
"constants": {
"AVAILABLE_PORTS_RANGE": [1024, 65535],
"TRACKER_ADDR": ["localhost", 12345],
"MAX_UDP_SEGMENT_DATA_SIZE": 65527,
"BUFFER_SIZE": 9216,
"CHUNK_PIECES_SIZE": 7216,
"MAX_SPLITTNES_RATE": 3,
"NODE_TIME_INTERVAL": 20,
"TRACKER_TIME_INTERVAL": 22
},
"tracker_requests_mode": {
"REGISTER": 0,
"OWN": 1,
"NEED": 2,
"UPDATE": 3,
"EXIT": 4
}
}
```

# V. Proposed approach

BitTorrent consists of two primary modules: (i) peers and (ii) the tracker. The
network includes multiple nodes (peers) and a single tracker. Each of these modules
will be explained in detail in the following sections.

## Peers

When a peer joins a torrent, it registers with the tracker and periodically updates the
tracker to confirm its continued participation in the torrent. The functionality of a peer
can be summarized in two primary functions:

## 1. Send (Upload)

A peer has the capability to send a chunk of a file to a neighboring peer. Before this
process occurs, the peer must first inform the torrent that it possesses a specific file.
Subsequently, the tracker updates its database, adding the peer as the owner of that
file. Once this is established, the peer is ready to send the file—specifically, a chunk
of the file—to another peer that has requested it. It is important to note that, at any
given time, a peer may send different chunks of various files to different neighboring
peers, which is made possible by the use of threads in programming languages. While
the peer listens for incoming requests, if a neighboring peer requests a file, it begins to
send the appropriate chunk of that file. A pertinent question arises: how does the peer
know which specific chunk of the file to send? This question will be addressed in the
following sections.

## 2. Download

Downloading a file involves two main steps. The first step, known as the "search"
step, requires the peer to inform the tracker of its request for a specific file. After
performing some processing (which will be explained in the following section), the
tracker provides a list of a fixed number of peers from which the file can be requested.

Assume that a request for downloading is sent to peer nodes for a file of size. Each of
the peer nodes will send/bytes of the file to the requesting peer in parallel. Once all
the file chunks have been gathered, they must be reassembled and saved in the local
directory of the requesting peer.


## Tracker

As previously mentioned, a torrent is managed by a single tracker, which maintains
general information about the peers involved. This information includes:

- The files possessed by each peer
- The address (IP and port number) of each peer in the torrent

The tracker’s database is periodically updated by the peers. Specifically, each node
sends a periodic message to the tracker to report its current state, and the tracker
updates its database accordingly through a polling mechanism. If a peer fails to
inform the tracker during one update cycle, it is assumed that the peer has left the
torrent, and its information is subsequently removed from the tracker’s database. As
outlined earlier, peers may send different types of messages to the tracker. These
messages can be categorized as follows:

| Mode      |     Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| *REGISTER*|     Tells the tracker that it is in the torrent.                                |
| *OWN*     |     Tells the tracker that it is now in sending mode for a specific file.       |
| *NEED*    |     Tells the torrent that it needs a file, so the file must be searched in the torrent. |
| *UPDATE*  |     Tells the tracker that its upload frequency rate must be incremented.       |
| *EXIT*    |     Tells the tracker that it left the torrent.                                 |


We now provide a brief overview of the actions taken by the tracker upon receiving
these messages:

```
REGISTER: The tracker receives this type of message under two conditions. First,
when a node joins the torrent, it sends this message to inform the tracker of its
participation. Second, at regular intervals (every 𝑖 seconds), a node sends this
message to confirm that it is still part of the torrent.
```
```
OWN: When a peer enters the "SEND" mode, it sends this message to the tracker,
which then updates its database to reflect the peer's ownership of the file within the
torrent.
```
```
NEED: When a peer requires a specific file, it sends this message to the tracker to
indicate its need for the file. The tracker then searches the torrent and ranks the peers
that own the file, using a sophisticated trading algorithm. The basic principle behind
this algorithm is that the tracker prioritizes peers that are currently uploading files at
the highest rate.
```
```
UPDATE: When a peer successfully sends a file to another node, its upload frequency
rate must be increased. This update is managed by the tracker.
```
```
EXIT: When a peer exits the torrent, all information related to that peer must be
removed from the tracker’s database.
How these steps work and how they are implemented are explained in the following
sections.
```
Mode Description
REGISTER Tells the tracker that it is in the torrent.
OWN Tells the tracker that it is now in sending mode for a specific file.
NEED Tells the torrent that it needs a file, so the file must be searched in the
torrent.
UPDATE Tells the tracker that it's upload frequency rate must be incremented.
EXIT Tells the tracker that it left the torrent.


# VI. Implementation detail

TorrentClient.py
There is a class named Node in node.py which has these fields:

```
Field Type Description
```
| Field            | Type           | Description                                                                 |
|------------------|----------------|-----------------------------------------------------------------------------|
| `node_id`        | `int`          | A unique ID of the node                                                    |
| `send_port`      | `int`          | A port for sending messages                                                |
| `rcv_socket`     | `socket.socket`| A socket for receiving messages                                            |
| `send_socket`    | `socket.socket`| A socket for sending messages                                              |
| `files`          | `list`         | A list of files which the node owns                                       |
| `is_in_send_mode`| `bool`         | A boolean variable which indicates whether the node is in send mode       |
| `downloaded_files`| `dict`        | A dictionary with filename as keys and a list of file owners to download from |

Upon executing the TorrentClient.py script, the run() function is called, initiating the
following actions:

1. An instance of the Node class is created, representing a new node.
2. The node informs the tracker of its entry into the torrent.
3. A thread is created, functioning as a timer to periodically send messages to the
    tracker, updating it with the node's current state.
4. Depending on the user's input command, the script invokes various functions,
    which will be discussed in the following sections.

We now describe the purpose of each function. These explanations have been kept
concise while ensuring they provide sufficient clarity and utility.

## Send mode functions:

```
def set_send_mode(self, filename: str) -> None:
```

- Send a message to the tacker to tells it that it has the file with name filename and is
ready to listen to other peers requests.
- Create a thread for listening to neighboring peers' requests. The thread calls``` listen()```
function.

```
def listen(self) -> None:
```
- It has a infinit loop for waiting for other peers' messages.
- Just after it receives a message, it calls ```handle_requests()```.

```
def handle_requests(self, msg: dict, addr: tuple) -> None:
```
- The messages from peers can be categorized to groups. First the one which are
asking for the size of a file. For this, we call ```tell_file_size()``` to calculate the size of the
file.
- In the second group, the nodes is asked for sending a chunk of a file. In this
condition, it calls ```send_chunk()```.

```
def tell_file_size(self, msg: dict, addr: tuple) -> None:
```
- This function is simple. It calculates the file using ```os.stat(file_path).stsize```.
- Then we send the result by sending a message of type None2Node.

```
def send_chunk(self, filename: str, rng: tuple, dest_node_id: int, dest_port: int) ->
None:
```
- Thus the chunk is splitted to multiple pieces to be transfarabale by calling
```split_file_to_chunks()```. It returns a list of pieces.
- Now we iterate the pieces and send them to the neighboring peer withing a UDP
segment. The piece is sent within a message of type ChunkSharing.

```
def split_file_to_chunks(self, file_path: str, rng: tuple) -> list:
```
- This function takes the range of the file which has to be splitted to pieces of fixed-
size (It this size can be modified in the configs.py). This is done by mmap.mmap()
which is a python built-in function.
- Then it returns the result as a list of chunk pieces.

```
def send_segment(self, sock: socket.socket, data: bytes, addr: tuple) -> None:
```
- All the messages which are transferring among peers uses this function to be sent. It
creates a UDPSegment instance and be sent with socket.socket functionalities.

```
def send_http_request(self, endpoint: str, payload: dict) -> dict:
```
- All the http messages except NEED message are transferring between peers and
tracker uses this function to be sent.

```
def send_https_request_download(self, tracker_url: str, payload: dict) -> dict:
```
- the http message that are transferring between peers and tracker in the download
process uses this function to be sent.

## Download mode functions:

```
def set_download_mode(self, torrent_filename: str) -> None:
```
- It first check if the node have the torrent file for download the corresponding file
- It then parse the torrent file for the filename and tracker url
- secondly, it check if the node has already owned this file. If yes, it returns.
- If No, it ask the tracker about the file owners.
- After getting the result from the tracker, it calls split_file_owners() to split the file to
equal-sized chunks.

```
def split_file_owners(self, file_owners: list, filename: str): -> dict
```
This is the most important function of this class. Til now we have the owner of the file
which we are going to download. We sort the owners based on their uploading
frequency rate. There are 5 main steps we have to follow:

1. First we must ask the size of the desired file from one of the file owners. This
    is done by calling the ```ask_file_size()```.
2. Now, we know the size, it's time to split it equally among peers to download
    chunks of it from them.
3. Now we iterate a thread for each neighbor peer to download a chunk from it.
    This done by iterating the threads and calling ```receive_chunk()``` for each
    individual one.
4. Now we have downloaded all the chunks of the file. It's time to sort them by
    calling ```sort_downloaded_chunks()```. Because they may have received in-
    ordered.
5. Finally, we assemble the chunks to re-build the file and saving it in the node
    directory. This is done by calling ```reassemble_file()```.

## Now let's see how each of these five functions work:

```
def ask_file_size(self, filename: str, file_owner: tuple) -> int:
```
- This function sends a Node2Node message to one of the neighboring peers for
asking the file size.

```
def receive_chunk(self, filename: str, range: tuple, file_owner: tuple):
```
- First we sends a ChunkSharing message to the neighboring peer to informs it that we
want that chunk.
- Then we wait for that chunk to be received.

```
def sort_downloaded_chunks(self, filename: str) -> list
```

- All the downloaded chunks are stored in self.downloaded_files. But they are in-
ordered and must be sorted. So we sort them based on theirs indices and return the
result as a ordered list.

```
def reassemble_file(self, chunks: list, file_path: str):
```
- this function is called to resemble the file

There are some more functions to be explained:

```
def inform_tracker_periodically(self, interval: int):
```
- As mentioned earlier, this function is called periodically to inform the state of the
node to the tracker by sending a http message.

```
def enter_torrent(self):
```
- It sends a HTTP message to the tracker to tells it that it enters the torrent.

```
def exit_torrent(self):
```
- It sends a HTTP message to the tracker to tells it that it left the torrent.

## tracker.py

the tracker module have the following fields:

```
Field Type Description
```
| Field               | Type         | Description                                                                 |
|---------------------|--------------|-----------------------------------------------------------------------------|
| `file_owners_list`  | `defaultdict`| A Python dictionary of the files with their owners in the torrent           |
| `send_freq_list`    | `defaultdict`| A Python dictionary of the nodes with their upload frequency rate           |
| `has_informed_tracker` | `defaultdict`| A Python dictionary of the nodes with a boolean variable indicating their status in the torrent |


send_freq_list defaultdict A python dictionary of the
nodes with their upload
frequency rate

has_informed_tracker defaultdict A python dictionary of the
nodes with a boolean
variable indicating their
status in the torren

By running tracker.py it per performs the following steps:

1. It first creates a thread to work as a timer, for checking the nodes status periodically
by calling ```check_nodes_periodically()```.
2. It start runing the tracker server

## Now we describe the purpose of each function:

```
def check_nodes_periodically( interval: int) -> None:
```
- Every T seconds, this function is called and it is responsible to check if the nodes are
still in the torrent.
- It iterates the has_informed_tracker and if its value is true for a peer, it means the
node has informed the tracker that is still in the torrent. In other hand, it it's value is
False, it means that specific node has left the torrent and its database must be removed
by calling ```remove_node()```.

```
def remove_node(msg) -> None:
```
- It removes all the information related to node with
id of node_id and address of addr in the tracker database.

```
def register_node(msg): -> None:
```
- It updates the has_informed_tracker dictionary for
a specific node.

```
def handle_node_request():
``` 
- This function is the heart of the Tracker class. Based on
message modes comes from the nodes, it calls different functions:

1. Mode OWN: It calls ```add_file_owner()```
2. Mode NEED: It calls ```search_file()```
3. Mode UPDATE: It calls ```update_db()```
4. Mode REGISTER: It updates the has_informed_tracker dictionary for a
    specific node.
5. Mode EXIT: It calls ```remove_node()```

```
def add_file_owner(msg) -> None:
```
- This function adds the node's file to the file_owners_list.

```
def search_file(msg) -> None:
```
- It iterates the self.file_owners_list to find the owners of the file which is needed.
Each owner will be appended to matched_entries list.
- It sends a HTTP message to the peer which has wanted from the tracker to search
for the file owners.

```
def update_db( msg):
```
- It's simple. It increments the send_freq_list dictionary for a file.

## There is also one other utility functions in Tracker module:

```
def save_db_as_json():
```

- We save the database into two separate JSON files: (i) nodes.json which contains the
information of nodes and theirs upload frequency rate, and (ii) files.json including the
information of files and their owners. Whenever some changes occur in the database
we call this function. These JSON files are in tracker_DB/ directory.

## utils.py

There are some helper functions in utils.py. All other python files have imported this
script.

```
def set_socket(port: int) -> socket.socket:
```
- This function takes a port number and creates a new UDP socket.

```
def free_socket(sock: socket.socket):
```
- This function takes a socket and frees a socket to be able to be used by others.

```
def generate_random_port() -> int:
```
- A function that generates a new(unused) random port number.

```
def parse_command(command: str):
```
- It parses the input command entered from the user.

```
def log(node_id: int, content: str, is_tracker=False) -> None:
```
- It is called several times by nodes and the tracker to log the events occurred in the
torrent. Each node has an individual log file in logs/ directory.

```
def calculate_file_hash(file_path):
```
- It calculate the file_hash for a file.

```
def create_torrent(file_path, output_path) -> None:
```
- It create a torrent file for a file

```
def parse_torrent_file(torrent_file_path):
```
- It parse the torrent file to obtain filename and tracker url.


# VII. Conclusion

Downloading large files, such as movies, music, games, or software, is a common
and engaging activity made efficient by the BitTorrent communication protocol,
which enables the distribution of large data chunks over the internet. In fact,
approximately one-third of internet traffic consists of BitTorrent data packets, making
it one of the most significant and widely-discussed topics in modern networking.

In this project, we have implemented a simplified version of BitTorrent using the
Python programming language. While BitTorrent has evolved significantly over the
years with various versions in use, this implementation covers the core modules of a
typical BitTorrent network, providing a useful introduction to how the protocol
operates.

Given the academic nature of this project, the code has not been tested in large-
scale environments. We would greatly appreciate any feedback you may have,
including the creation of issues or pull requests, should you encounter any problems
or misunderstandings.


