from os import remove
import socket
import threading

HOST = socket.gethostbyname(socket.gethostname())

try:
    with open("password.txt", "r") as f:
        PASSWORD = str(f.read())

    with open("admin_password.txt", "r") as f:
        ADMN_PASSWORD = str(f.read())

    with open("server_port.txt", "r") as f:
        PORT = int(f.read())
except:
    print("Failed to load details. Using default login info.")
    PASSWORD = "1234"
    ADMN_PASSWORD = "admin"
    PORT = 2526

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

                ########################
                ### Command handling ###
                ########################

                # Disconnect the user who sent the command
                if(cmd[0].lower() == "leave" or cmd[0].lower() == "l"):
                    index = clients.index(client)
                    nickname = nicknames[index]
                    nicknames.remove(nickname)
                    clients.remove(client)
                    
                    client.send("You left the server. Bye!".encode("utf-8"))

                    client.send("cnnctn_end".encode("utf-8"))
                    broadcast(f"[SERVER<TO@all>] {nickname} left the chat room!".encode('utf-8'))
                    print(f"{nickname} left the chat!")
                    break
                
                # Return a list of all commands
                elif(cmd[0].lower() == "help"):
                    client.send("\nCommands:\n---------\nhelp        - all commands\nAmIAdmin    - see if you're an admin\nleave (or l)- leave the chat room\nlist        - see all users in the chat room\n\nADMIN commands:\n---------------\nkick <username>\n".encode("utf-8"))

                # Return if the user who sent the command is an administrator
                elif(cmd[0].lower() == "amiadmin"):
                    if(client in admins):
                        client.send("You are an ADMIN on this server!".encode("utf-8"))
                    else:
                        client.send("Unfortunetly you are not an ADMIN.".encode("utf-8"))

                # Return all users who are online in this chat room
                if(cmd[0].lower() == "list"):
                    all_users = "All users in this chat room:\n----------------------------\n\n"
                    for user in nicknames:
                        all_users += user
                        all_users += "\n"
                    client.send(all_users.encode('utf-8'))

                # Kick a user by providing a username
                if(cmd[0].lower() == "kick"):
                    if(client in admins and cmd[1] in nicknames):
                        user = clients[nicknames.index(cmd[1])]
                        user.send(f"You have been kicked from the server by {nicknames[clients.index(client)]}. Don't be mad.".encode("utf-8"))
                        user.send("cnnctn_end".encode("utf-8"))
                        user.close()

                        client.send(f"You kicked {nicknames[clients.index(user)]}!".encode("utf-8"))
                    else:
                        client.send("You can't perform this action!".encode("utf-8"))

            else:
                message = f"{nicknames[clients.index(client)]} >>> {message}"
                broadcast(message.encode("utf-8"))

        # Error handling - For example a client left the chat room without closing the tcp connection properly
        except:
            index = clients.index(client)
            nickname = nicknames[index]
            nicknames.remove(nickname)
            if(client in admins): admins.remove(client)
            clients.remove(client)

            client.close()

            broadcast(f"[SERVER<TO@all>] {nickname} left the chat room!".encode('utf-8'))
            print(f"{nickname} left the chat!")
            print(f"All clients left: {nicknames}")
            break

def receive():
    print(f"Host connection details are: {HOST}:{PORT} | security key: {PASSWORD} | ADMIN key: {ADMN_PASSWORD}")
    print("Server is listening...")
    while True:
        try:
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
                if(nickname in nicknames):
                    client.send(f"Username '{nickname}' is already used in this chat room. Better luck next time!".encode("utf-8"))
                    client.send("cnnctn_end".encode("utf-8"))
                    client.close()
                    continue
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
        except:
            print("Error while client connecting! pass...")
            pass

# RUN THE SERVER
receive()