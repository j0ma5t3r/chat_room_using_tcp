import socket
import threading
import string
import random
import os

file_dir = os.path.dirname(os.path.realpath(__file__))

random_token_len = 10

HOST = socket.gethostbyname(socket.gethostname())

try:
    with open(f"{file_dir}/server_password.txt", "r") as f:
        PASSWORD = str(f.read())

    with open(f"{file_dir}/server_admin_password.txt", "r") as f:
        ADMN_PASSWORD = str(f.read())

    with open(f"{file_dir}/server_port.txt", "r") as f:
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
admin_commands = ["kick", "op", "unop", "pwd"]

invites = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024).decode("utf-8")

            ########################
            ### Command handling ###
            ########################

            if(message.startswith("!") and not message == "!"):
                cmd = message.split("!")
                cmd = str(cmd[1]).split(" ")
                print(cmd)

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
                    print(f"All clients left: {nicknames}")
                    break
                
                # Return a list of all commands
                elif(cmd[0].lower() == "help"):
                    client.send("\nCommands:\n---------\nhelp        - all commands\nAmIAdmin    - see if you're an admin\nleave (or l)- leave the chat room\nlist        - see all users in the chat room\ninvite      - create an one-time invite\n\nADMIN commands:\n---------------\nkick <username>\nop <username>\nunop <username>\npwd <string>\n".encode("utf-8"))

                # Return if the user who sent the command is an administrator
                elif(cmd[0].lower() == "amiadmin"):
                    if(client in admins):
                        client.send("You are an ADMIN on this server!".encode("utf-8"))
                    else:
                        client.send("Unfortunetly you are not an ADMIN.".encode("utf-8"))

                # Return all users who are online in this chat room
                elif(cmd[0].lower() == "list"):
                    all_users = "All users in this chat room:\n----------------------------\n\n"
                    for user in nicknames:
                        all_users += user
                        all_users += "\n"
                    client.send(all_users.encode('utf-8'))

                # Create an one-time password for a "normal" user to log in
                elif(cmd[0].lower() == "invite"):
                    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = random_token_len))
                    print(f"Invite token is: {ran}")
                    global invites
                    invites.append(ran)
                    client.send(f"You generated the token >>> {ran} <<< give it wisely to another user who wants to join.".encode("utf-8"))

                ### ADMIN commands ###
                if(client in admins and cmd[0].lower() in admin_commands):

                    # Kick a user by providing a username
                    if(cmd[0].lower() == admin_commands[0] and cmd[1] in nicknames and len(cmd > 1)):
                        user = clients[nicknames.index(cmd[1])]
                        user.send(f"You have been kicked from the server by {nicknames[clients.index(client)]}. Don't be mad.".encode("utf-8"))
                        user.send("cnnctn_end".encode("utf-8"))
                        user.close()

                        client.send(f"You kicked {nicknames[clients.index(user)]}!".encode("utf-8"))

                    # Promote a user to ADMIN by providing a username
                    elif(cmd[0].lower() == admin_commands[1] and cmd[1] in nicknames and not clients[nicknames.index(cmd[1])] in admins) and len(cmd > 1):
                        user = clients[nicknames.index(cmd[1])]
                        admins.append(user)

                        client.send(f"You promoted {cmd[1]} to ADMIN!".encode("utf-8"))
                        user.send("You have been promoted to ADMIN! Don't be a fool!".encode("utf-8"))
                    
                    # Un-op a user
                    elif(cmd[0].lower() == admin_commands[2] and clients[nicknames.index(cmd[1])] in admins and len(cmd > 1)):
                        user = clients[nicknames.index(cmd[1])]
                        admins.remove(user)

                        client.send(f"You removed {cmd[1]} from the ADMINs!".encode("utf-8"))
                        user.send("You are no longer an ADMIN.".encode("utf-8"))
                    
                    # Set a new server password
                    elif(cmd[0].lower() == admin_commands[3] and len(cmd) > 1):
                        with open(f"{file_dir}\server_password.txt", "w") as f:
                            f.write(cmd[1])
                        global PASSWORD
                        PASSWORD = cmd[1]
                        print(f"New server password is: {cmd[1]}")
                        broadcast(f"The server password has been changed by {nicknames[clients.index(client)]}!".encode("utf-8"))

                else:
                    if(cmd[0].lower() in admin_commands):
                        client.send("You can't perform this action!".encode("utf-8"))
                    else:
                        pass
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
            try:
                client.send("cnnctn_end".encode("utf-8"))
            except:
                pass
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
            if(not cl_passwd == PASSWORD and not cl_passwd == ADMN_PASSWORD and not cl_passwd in invites):
                print(f"Password received from client {address[0]}: '{cl_passwd}' - !!!>REJECTED<!!!, closing connection...")
                client.send("Wrong password.".encode("utf-8"))
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
                elif(" " in nickname):
                    client.send(f"Your username insn't allowed to contain spaces.".encode("utf-8"))
                    client.send("cnnctn_end".encode("utf-8"))
                    client.close()
                    continue

                nicknames.append(nickname)
                clients.append(client)

                # Add client to admins if they returned the admin password
                if(cl_passwd == ADMN_PASSWORD):
                    admins.append(client)
                
                if(cl_passwd in invites): 
                    invites.remove(cl_passwd)
                    print(f"'{cl_passwd}' was used and removed from 'invites'.")

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