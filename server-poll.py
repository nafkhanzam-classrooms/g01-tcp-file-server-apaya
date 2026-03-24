import socket
import select
import os
import time

HOST, PORT = '127.0.0.1', 5000
os.makedirs("uploads", exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

try:
    poller = select.poll()
except AttributeError:
    print("PERINGATAN: OS ini tidak mendukung select.poll(). Gunakan Linux/WSL.")
    exit()

poller.register(server, select.POLLIN)
fd_to_socket = {server.fileno(): server}

print(f"Server Poll jalan di {PORT}...")

while True:
    events = poller.poll(1000)
    for fd, flag in events:
        s = fd_to_socket[fd]
        if flag & select.POLLIN:
            if s is server:
                conn, addr = s.accept()
                poller.register(conn, select.POLLIN)
                fd_to_socket[conn.fileno()] = conn
            else:
                try:
                    data = s.recv(1024).decode('utf-8')
                    if data:
                        if data == "/list":
                            s.send(f"Files: {', '.join(os.listdir('uploads'))}".encode('utf-8'))
                        elif data.startswith("/upload"):
                            filename = data.split()[1]
                            time.sleep(0.5)
                            file_data = s.recv(4096)
                            with open(os.path.join("uploads", filename), "wb") as f:
                                f.write(file_data)
                        elif data.startswith("/download"):
                            filename = data.split()[1]
                            filepath = os.path.join("uploads", filename)
                            if os.path.exists(filepath):
                                s.send(f"FILE_READY:{filename}".encode('utf-8'))
                                time.sleep(0.5)
                                open(filepath, "rb")
                                with open(filepath, "rb") as f:
                                    s.sendall(f.read())
                        else:
                            for fd_client in fd_to_socket:
                                c = fd_to_socket[fd_client]
                                if c is not server and c is not s:
                                    c.send(f"Pesan: {data}".encode('utf-8'))
                    else:
                        poller.unregister(s)
                        s.close()
                        del fd_to_socket[fd]
                except:
                    poller.unregister(s)
                    s.close()
                    del fd_to_socket[fd]