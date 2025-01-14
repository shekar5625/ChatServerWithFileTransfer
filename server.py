import socket
import threading

HOST = '127.0.0.1'
PORT = 12345
clients = {}
usernames = {}

def handle_client(client_socket, client_address):
    username = client_socket.recv(1024).decode('utf-8')
    clients[client_socket] = username
    usernames[username] = client_socket

    print(f"[NEW CONNECTION] {username} ({client_address}) connected.")

    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            
            if message.startswith("/sendfile"):
                _, target_username, filename = message.split(' ', 2)
                if target_username in usernames:
                    forward_file_message(sender_socket=client_socket, receiver_socket=usernames[target_username], filename=filename.strip())
                else:
                    client_socket.send(f"User {target_username} not found.".encode('utf-8'))
            
            elif message.startswith("@"):
                target_username, private_msg = parse_private_message(message)
                if target_username in usernames:
                    send_private_message(private_msg, usernames[target_username], username)
                else:
                    client_socket.send(f"User {target_username} not found.".encode('utf-8'))
            else:
                broadcast(message, client_socket, username)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        remove_client(client_socket)

def parse_private_message(message):
    split_msg = message.split(' ', 1)
    target_username = split_msg[0][1:]  # Remove '@' prefix
    private_msg = split_msg[1] if len(split_msg) > 1 else ''
    return target_username, private_msg

def send_private_message(message, target_socket, sender_username):
    target_socket.send(f"[PRIVATE] {sender_username}: {message}".encode('utf-8'))

def broadcast(message, client_socket, username):
    for client in clients:
        if client != client_socket:
            try:
                client.send(f"{username}: {message}".encode('utf-8'))
            except:
                remove_client(client)

def remove_client(client_socket):
    if client_socket in clients:
        print(f"[DISCONNECTED] {clients[client_socket]} disconnected.")
        client_socket.close()
        del usernames[clients[client_socket]]
        del clients[client_socket]

def forward_file_message(sender_socket, receiver_socket, filename):
    sender_socket.send(f"Sending {filename} to {clients[receiver_socket]}...".encode('utf-8'))
    receiver_socket.send(f"Receiving {filename} from {clients[sender_socket]}...".encode('utf-8'))

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    start_server()
