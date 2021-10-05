import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 9090))
sock.listen(1)
conn, addr = sock.accept()
print('connected:', addr)
while True:
    data = conn.recv(1024).decode()
    if not data:
        break
    if data == 'Hello':
        data = 'Hello from server'
    conn.send(data.upper().encode())
conn.close()
