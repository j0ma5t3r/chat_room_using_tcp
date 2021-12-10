import socket
import threading

HOST = '192.168.178.70'
PORT = 2526

stop_threads = False

nickname = str(input("Choose a nickname     >>> "))
passwd = str(input("Enter server password >>>"))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    global stop_threads
    while True:
        if stop_threads:
            break
        try:
            message = client.recv(1024).decode('utf-8')
            if(message == "return_nick"):
                client.send(nickname.encode('utf-8'))
            elif(message == "return_passwd"):
                client.send(passwd.encode('utf-8'))
            elif(message == "cnnctn_end"):
                print("CONNECTION CLOSED BY SERVER, quit...")
                stop_threads = True
            else:
                print(message)
        
        except:
            print("A error occured!")
            client.close()
            break

def write():
    while True:
        if stop_threads:
            break
        message = str(input(''))
        client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()