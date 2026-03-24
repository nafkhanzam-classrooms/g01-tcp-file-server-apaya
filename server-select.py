import socket
import select
import os
import time

HOST, PORT = '127.0.0.1', 5000
os.makedirs("uploads", exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind((HOST, PORT))
server.listen(5)
inputs = [server]

print(f"Server Select jalan di {PORT}...")

while True:
    readable, _, _ = select.select(inputs, [], [])
    for s in readable:
        if s is server:
            conn, addr = s.accept()
            conn.setblocking(0)
            inputs.append(conn)
        else:
            try:
                data = s.recv(1024).decode('utf-8')
                if data:
                    if data == "/list":
                        s.send(f"Files: {', '.join(os.listdir('uploads'))}".encode('utf-8'))
                    elif data.startswith("/upload"):
                        filename = data.split()[1]
                        # Karena non-blocking, kita tunggu sebentar untuk file data
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
                            with open(filepath, "rb") as f:
                                s.sendall(f.read())
                    else:
                        for c in inputs:
                            if c is not server and c is not s:
                                c.send(f"Pesan: {data}".encode('utf-8'))
                else:
                    inputs.remove(s)
                    s.close()
            except:
                inputs.remove(s)
                s.close()