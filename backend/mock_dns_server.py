import socket

# Store id -> IP mappings
registry = {}

# UDP setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 12347))  # Listen on port 12347

print("Mock DNS server running on port 12347")

while True:
    data, addr = sock.recvfrom(1024)
    text = data.decode().strip()

    print("received ",text)
    
    if text.startswith("REGISTER "):
        # Format: REGISTER id
        name = text.split(maxsplit=1)[1]
        registry[name] = addr[0]  # Save sender's IP
        sock.sendto(b"OK", addr)
        print("REGISTER",name,addr[0])
    
    elif text.startswith("RESOLVE "):
        # Format: RESOLVE id
        name = text.split(maxsplit=1)[1]
        ip = registry.get(name, "NOT_FOUND")
        sock.sendto(ip.encode(), addr)
        print("RESOLVE", name , ip)
    
    else:
        sock.sendto(b"ERROR Unknown command", addr)
