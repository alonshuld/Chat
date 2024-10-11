import socket
import threading


HOST_IP_ADR = "localhost"
PORT = 13377
BUFFER_SIZE = 1024
NICKNAME_LEN = 8


class Clients:
    _clients = []
    _nicknames = []
    _room = []
    _all_rooms = []


    def validNickname(self, nickname: str):
        if nickname in self._nicknames:
            return f"Invalid nickname, already taken", False
        if len(nickname) == 0 or len(nickname) > NICKNAME_LEN:
            return f"Invalid nickname, max length is {NICKNAME_LEN}", False
        for char in nickname:
            if not ('0' <= char <= '9' or \
                'a' <= char <= 'z' or \
                'A' <= char <= 'Z'):
                return f"Invalid nickname, only [a-z], [A-Z], [0-9]", False
        return f"Hello {nickname}", True
    

    def validRoomName(self, room_name: str):
        if room_name in self._all_rooms:
            return f"Invalid room name, already taken", False
        if len(room_name) == 0 or len(room_name) > NICKNAME_LEN:
            return f"Invalid room name, max length is {NICKNAME_LEN}", False
        for char in room_name:
            if not ('0' <= char <= '9' or \
                'a' <= char <= 'z' or \
                'A' <= char <= 'Z'):
                return f"Invalid room name, only [a-z], [A-Z], [0-9]", False
        return "Your wellcome!", True
    

    def roomsMenu(self) -> str:
        ans = "Select:\n0. Open your own room\n"
        if len(self._all_rooms) == 0:
            return ans + "No opened rooms yet\n"
        for i in range(len(self._all_rooms)):
            ans += f"{i + 1}. {self._all_rooms[i]}\n"
        return ans
    

    def clientRemoving(self, client) -> None:
        i = self._clients.index(client)
        self._clients.pop(i)


    def broadcast(self, client, room: int, msg: str):
        for i in range(len(self._room)):
            if self._room[i] == room and self._clients[i] != client:
                self._clients[i].send(msg.encode())



def connection_handler(server: socket.socket, clients: Clients):
    while True:
        try:
            nickname = ""

            # Accepting new client
            client, address = server.accept()

            # Printing to log about new connection
            print(f"Connection established: {str(address)}")

            # Getting a username for the client
            valid = False
            client.send(f"Please enter your nickname: ".encode())
            while not valid:
                nickname = client.recv(BUFFER_SIZE).decode()
                ans, valid = clients.validNickname(nickname)
                client.send(ans.encode())

            # Printing rooms menu
            client.send(clients.roomsMenu().encode())
            room = client.recv(BUFFER_SIZE).decode()

            # Choosing room
            while not room.isnumeric() or int(room) < 0 or int(room) > len(clients._all_rooms):
                client.send("Unavailable room!".encode())
                room = client.recv(BUFFER_SIZE).decode()
            room = int(room)

            # Opening new room
            if room == 0:

                # Choosing new room name
                client.send(f"Please enter room name: ".encode())
                valid = False
                while not valid:
                    room_name = client.recv(BUFFER_SIZE).decode()
                    ans, valid = clients.validRoomName(room_name)
                    client.send(ans.encode())
                
                clients._all_rooms.append(room_name)
                room = clients._all_rooms.index(room_name)
            
            else:
                room -= 1
            
            # Printing to log
            print(f"Joined: '{nickname}'\t\tRoom: {clients._all_rooms[room]}")

            # Adding to lists
            clients._clients.append(client)
            clients._nicknames.append(nickname)
            clients._room.append(room)

            thread = threading.Thread(target=chat_handler, args=(client, room, clients))
            thread.start()

        except Exception:
            print(f"Connection lost: {str(address)}")
            client.close()


def chat_handler(client, room: int, clients: Clients) -> None:
    while True:
        try:
            # Recive message
            msg = client.recv(BUFFER_SIZE).decode()
            # Send it to the other connected clients in the chat
            clients.broadcast(client, room, f"{clients._nicknames[clients._clients.index(client)]}: {msg}")
        except:
            # Remove all the user's data
            i = clients._clients.index(client)
            clients._clients.remove(client)
            client.close()
            nickname = clients._nicknames[i]
            clients._nicknames.remove(nickname)
            clients._room.pop(i)
            # Send a message to the other connected clients in the chat 
            clients.broadcast(None, room, f"{nickname} has left the chat!")
            # Print to log that the user has left
            print(f"Left: '{nickname}'\t\tRoom: {clients._all_rooms[room]}")
            break


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_IP_ADR, PORT))
    server.listen()

    clients = Clients()

    print("Server started!")
    connection_handler(server, clients)


if __name__ == "__main__":
    main()
