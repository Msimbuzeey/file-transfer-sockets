# VERSION 4.8.25

import socket
from pathlib import Path

# SERVER_HOST_IP = "10.108.223.150"
SERVER_HOST_IP = "localhost"
PORT = 33456

# This is just part of the custom protocol for this operation
# Used as a flag that tells the client upon reception that Im about to send a file
# After-wards the protocol used, sends the file name, and its size(used to calculate progress), then the file bytes sequence
FILE_START_SEND_FLAG = "FSSG"


def send_file(tx_file: Path, client_socket: socket, tx_file_name: str = None):
    if tx_file_name is None:
        tx_file_name = tx_file.name

    tx_file_size = tx_file.stat().st_size

    # Sending the file name so the receiver knows what name to save the file with
    # Also sending the size, used for progress
    client_socket.sendall(bytes(f"{FILE_START_SEND_FLAG}{tx_file_name}|{tx_file_size}", "utf-8"))

    with open(tx_file, "rb") as tx_file:
        print(f"Sending file: [{tx_file_name}]")
        total_bytes_tx = client_socket.sendfile(tx_file)
        print(f"DONE: Sent {total_bytes_tx} bytes")


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((SERVER_HOST_IP, PORT))

        print("SERVER STARTED")
        server.listen()
        print("LISTENING...")

        c_skt, client_addr = server.accept()
        print(f"CONNECTED TO {client_addr}")

        with c_skt:
            while True:
                file_to_tx = Path(input("File To Send: "))

                if not file_to_tx.exists():
                    print("Error! file doesn't exist")
                    continue

                # The script allows sending files and folders, decided to use separation of concerns
                # and decoupled the file sending logic, then use separate code for logic of sending folders
                # If the provided path is a file, then just send normallly
                if file_to_tx.is_file():
                    send_file(file_to_tx, c_skt)

                # If the path provided is a directory(folder), then we have to reiterate through all subdirectories
                # under it and iteratively send each file in order to properly recreate the folder at the receiving end
                # 2 ways to do this
                #   1) Zip the folder and send it as a file, then unzip at receiver(Simpler, Cleaner).
                #   Didn't do this, cause that would require using zipfile library and extra logic outside scope of this
                #   script, but feel free to do so in your implementation
                #   2) Recursively iterate through subdirs, using either os.walk or this method below
                elif file_to_tx.is_dir():
                    # Basically walks through a Path's subdirectories and files(equivalent to os.walk)
                    for file_node in file_to_tx.rglob("*"):
                        if file_node.is_file():
                            # Build a relative path like: "folder/subfolder/file.txt"
                            rel_path = file_node.relative_to(file_to_tx.parent)
                            send_file(file_node, c_skt, tx_file_name=rel_path)
