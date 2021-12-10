import socket
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 2526
PASSWORD = "1234"
ADMN_PASSWORD = "admin"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen(10)

clients = []
nicknames = []
admins = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024).decode("utf-8")

            if(message.startswith("!") and not message == "!"):
                cmd = message.split("!")
                cmd = str(cmd[1]).split(" ")
                print(cmd)

                # Command handling
                if(cmd[0].lower() == "leave"):
                    kick(client)
                    break

                elif(cmd[0].lower() == "amiadmin"):
                    if(client in admins):
                        client.send("You are an ADMIN on this server!".encode("utf-8"))
                    else:
                        client.send("Unfortunetly you are not an ADMIN.".encode("utf-8"))

                if(cmd[0].lower() == "kick"):
                    if(client in admins):
                        kick(clients[nicknames.index(cmd[1])])
                    else:
                        client.send("You can't perform this action!".encode("utf-8"))

            else:
                message = f"{nicknames[clients.index(client)]} >>> {message}"
                broadcast(message.encode("utf-8"))
        except:
            print("E R R O R ! ! !")
            if(client in clients):
                kick(client)
            break

def receive():
    print(f"Host connection details are: {HOST}:{PORT} | security key: {PASSWORD} (not yet implemented)")
    print("Server is listening...")
    while True:
        client, address = server.accept()
        print(f"Client connected with ip address {address[0]}")

        client.send('return_passwd'.encode('utf-8'))
        cl_passwd = client.recv(1024).decode("utf-8")
        if(not cl_passwd == PASSWORD and not cl_passwd == ADMN_PASSWORD):
            print(f"Password received from client {address[0]}: '{cl_passwd}' - !!!>REJECTED<!!!, closing connection...")
            client.send("cnnctn_end".encode("utf-8"))
            client.close()
            print("Connection closed!")
        else:
            print(f"Password received from client {address[0]}: '{cl_passwd}' - !!!>ACCEPTED<!!!, continue...")
            client.send('return_nick'.encode("utf-8"))
            nickname = client.recv(1024).decode("utf-8")
            nicknames.append(nickname)
            clients.append(client)

            # Add client to admins if they returned the admin password
            if(cl_passwd == ADMN_PASSWORD):
                admins.append(client)

            print(f"Nickname of client {address[0]} is: {nickname}")
            broadcast(f"[SERVER<TO@all>] {nickname} joined your party!".encode("utf-8"))
            client.send(f"[SERVER<TO@you>] Connected to the server {HOST} as {nickname}!".encode("utf-8"))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

def kick(client):
    index = clients.index(client)
    client.send("YOU HAVE BENN KICKED FROM THE SERVER!".encode("utf-8"))
    client.send("cnnctn_end".encode("utf-8"))
    client.close()
    nickname = nicknames[index]
    broadcast(f"[SERVER<TO@all>] {nickname} left the chat room!".encode('utf-8'))
    print(f"{nickname} left the chat!")
    nicknames.remove(nickname)
    clients.remove(client)

# RUN THE SERVER
receive()