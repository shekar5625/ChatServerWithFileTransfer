import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if "Receiving" in message:
                _, filename = message.split(' ', 1)
                receive_file(client_socket, filename.strip())
            else:
                print(message)
        except Exception as e:
            print(f"[ERROR] {e}")
            client_socket.close()
            break

def receive_file(client_socket, filename):
    with open(f"received_{filename}", 'wb') as file:
        while True:
            chunk = client_socket.recv(1024)
            if chunk == b"EOF":
                break
            if not chunk:
                break
            file.write(chunk)
    print(f"File {filename} received and saved as received_{filename}.")

def send_messages(client_socket):
    while True:
        message = input()
        
        if message.startswith("/sendfile"):
            try:
                _, target_username, filename = message.split(' ', 2)
                client_socket.send(message.encode('utf-8'))
                # Wait for server confirmation before sending file
            except ValueError:
                print("Invalid file sending command. Use: /sendfile <username> <filename>")
        else:
            client_socket.send(message.encode('utf-8'))

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Failed to connect to the server. Please ensure the server is running.")
        return

    username = input("Enter your username: ")
    client_socket.send(username.encode('utf-8'))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    send_thread.start()

if __name__ == "__main__":
    start_client()
