import socket
import os
import time

HOST, PORT = '127.0.0.1', 5000
os.makedirs("uploads", exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"Server Sync jalan di {PORT} (Hanya 1 client)...")

while True:
    conn, addr = server.accept()
    print(f"Terhubung dengan {addr}")
    with conn:
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                if not data: break
                
                if data == "/list":
                    conn.send(f"Files: {', '.join(os.listdir('uploads'))}".encode('utf-8'))
                elif data.startswith("/upload"):
                    filename = data.split()[1]
                    with open(os.path.join("uploads", filename), "wb") as f:
                        f.write(conn.recv(4096))
                    conn.send("Upload sukses.".encode('utf-8'))
                elif data.startswith("/download"):
                    filename = data.split()[1]
                    filepath = os.path.join("uploads", filename)
                    if os.path.exists(filepath):
                        conn.send(f"FILE_READY:{filename}".encode('utf-8'))
                        time.sleep(0.5)
                        with open(filepath, "rb") as f:
                            conn.sendall(f.read())
            except:
                break
    print("Client keluar. Siap terima client baru.")