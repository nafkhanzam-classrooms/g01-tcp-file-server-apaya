import socket
import threading
import os
import time

def receive_messages(client_socket):
    while True:
        try:
            header = client_socket.recv(1024)
            if not header: break
            
            try:
                message = header.decode('utf-8')
                if message.startswith("FILE_READY:"):
                    filename = message.split(":")[1]
                    print(f"\n[Mendownload {filename} dari server...]")
                    
                    file_data = client_socket.recv(4096)
                    with open("dl_" + filename, "wb") as f:
                        f.write(file_data)
                    print(f"[Sukses] File tersimpan sebagai dl_{filename}\n> ", end="")
                else:
                    print(f"\n[SERVER]: {message}\n> ", end="")
            except UnicodeDecodeError:
                pass
        except:
            print("\nKoneksi terputus.")
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 5000))

    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.daemon = True
    thread.start()

    print("Command: /list, /upload <nama_file>, /download <nama_file>")
    while True:
        msg = input("> ")
        if msg.startswith("/upload"):
            parts = msg.split()
            if len(parts) >= 2 and os.path.exists(parts[1]):
                client.send(msg.encode('utf-8'))
                time.sleep(0.5) 
                with open(parts[1], "rb") as f:
                    client.sendall(f.read())
                print("File terkirim!")
            else:
                print("File tidak ditemukan di komputer kamu!")
        else:
            client.send(msg.encode('utf-8'))

if __name__ == "__main__":
    start_client()