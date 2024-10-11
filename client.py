import socket
import threading


SERVER_IP_ADR = 'localhost'
SERVER_PORT = 13377
BUFFER_SIZE = 1024 


def read_chat(client: socket.socket) -> None:
    while True:
        try:
            msg = client.recv(BUFFER_SIZE).decode().strip()
            if msg:
                print(msg)
        except:
            client.close()
            print("An error has occured! Disconnected!")
            break


def write_chat(client: socket.socket) -> None:
    while True:
        client.send(input("").encode())


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP_ADR, SERVER_PORT))
    except:
        print("Couldn't connect to the server!")

    write_thread = threading.Thread(target=write_chat, args=(client,))
    write_thread.start()

    read_chat(client)


if __name__ == "__main__":
    main()