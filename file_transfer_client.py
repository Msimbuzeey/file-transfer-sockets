# VERSION 4.8.25

import socket
from pathlib import Path

# SERVER_HOST_IP = "10.124.2.82"
SERVER_HOST_IP = "localhost"

PORT = 33456

FILE_START_SEND_FLAG = "FSSG"
FILE_SAVE_PATH = "received/"

FILE_RX_BUFFER_SIZE = 1024


def receive_file_loop(client_skt: socket.socket, rx_file_name: str, rx_file_size: int):
    print(f"Receiving File: {rx_file_name}({unit_placer(rx_file_size)})", end="")

    rx_file_path = Path(FILE_SAVE_PATH) / Path(rx_file_name)
    rx_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(rx_file_path, "wb+") as rx_file:
        rx_data_size = 0
        # Read file data or download the file in chunks of 1KB(1024bytes)
        print("...")
        rx_progress = 0
        while True:
            frx_data = client_skt.recv(FILE_RX_BUFFER_SIZE)
            frx_data_size = len(frx_data)

            rx_file.write(frx_data)

            # FILE TRANSFER PROGRESS
            rx_data_size += len(frx_data)

            if rx_file_size != 0:
                rx_progress = (rx_data_size / rx_file_size) * 100
            print(f"\r{unit_placer(rx_data_size)}/{unit_placer(rx_file_size)} ({rx_progress:.2f}%)", end="")

            if rx_data_size >= rx_file_size:
                print("File Transfer Complete")
                break
    print()


def unit_placer(quantity, units: tuple = ("B", "KB", "MB")):
    """
    Scale data_bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in units:
        if quantity < factor:
            return f"{quantity:.2f}{unit}"
        quantity /= factor


if __name__ == '__main__':
    with socket.socket() as client:
        client.connect((SERVER_HOST_IP, PORT))
        print("CONNECTED")

        while True:
            rx_data: str = client.recv(FILE_RX_BUFFER_SIZE).decode("utf-8")  # RECEIVED DATA

            if rx_data.startswith(FILE_START_SEND_FLAG):
                file_rx_metadata = rx_data.removeprefix(FILE_START_SEND_FLAG).strip()
                file_rx_metadata = file_rx_metadata.split("|")
                rx_f_name, rx_f_size = file_rx_metadata[0], int(file_rx_metadata[1])

                receive_file_loop(client_skt=client, rx_file_name=rx_f_name, rx_file_size=rx_f_size)
