import socket
import threading
import os
import time

file_dir = os.path.dirname(os.path.realpath(__file__))

try:
    with open(f"{file_dir}/client_host_ip.txt", "r") as f:
        HOST = str(f.read())

    with open(f"{file_dir}/client_host_port.txt", "r") as f:
        PORT = int(f.read())
except:
    print("Failed to load details. Using default login info.")
    HOST = "localhost"
    PORT = 2526

print(f"Host connection: {HOST}:{PORT}")

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
            elif(message == "perform_ping_test"):
                print(f"Your ping to {HOST}:{PORT} is: {ping()} ms")
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

def ping():
    while True:
        start_time = time.time()
        client.send("ping-test-msg".encode('utf-8'))
        msg = client.recv(1024)
        stop_time = time.time()
        if(msg.decode("utf-8") == "ping-answr"):
            break
    return stop_time - start_time

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()