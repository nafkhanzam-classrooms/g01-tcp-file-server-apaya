import socket
import threading
import os
import time

HOST, PORT = '127.0.0.1', 5000
os.makedirs("uploads", exist_ok=True)
clients = []

def broadcast(message, current_client):
    for c in clients:
        if c != current_client:
            try: c.send(message)
            except: clients.remove(c)

def handle_client(conn):
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data: break

            if data == "/list":
                files = os.listdir("uploads")
                conn.send(f"Files: {', '.join(files)}".encode('utf-8'))
            elif data.startswith("/upload"):
                filename = data.split()[1]
                file_data = conn.recv(4096)
                with open(os.path.join("uploads", filename), "wb") as f:
                    f.write(file_data)
                broadcast(f"File {filename} diupload.".encode('utf-8'), conn)
            elif data.startswith("/download"):
                filename = data.split()[1]
                filepath = os.path.join("uploads", filename)
                if os.path.exists(filepath):
                    conn.send(f"FILE_READY:{filename}".encode('utf-8'))
                    time.sleep(0.5)
                    with open(filepath, "rb") as f:
                        conn.sendall(f.read())
                else:
                    conn.send("File tidak ada di server.".encode('utf-8'))
            else:
                broadcast(f"Pesan: {data}".encode('utf-8'), conn)
        except:
            break
    clients.remove(conn)
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"Server Thread jalan di {PORT}...")

while True:
    conn, addr = server.accept()
    clients.append(conn)
    threading.Thread(target=handle_client, args=(conn,)).start()