import cv2
import socket
import struct


def send_udp_broadcast(message ):
    # send a broadcast with the message
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(message, ("255.255.255.255", 12347))
    sock.settimeout(3)  # Optional: avoid blocking forever
    
    #send ACK and return value or return none
    try:
        response, _ = sock.recvfrom(1024)
        sock.close()
        return response.decode()
    except TimeoutError:
        sock.close()
        return None

# Wait until ipaddress is registered on mock dns server
resp=None
while( resp is None):
    resp=send_udp_broadcast(b"REGISTER backend")

# port of the BitDogLab plate 
PORT_XY = 12345
bitdog_ip=None

# Setup socket connection UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Load OpenCV face detector

# Open CV Pretrained model for faces
# Arch linux #####
cascade_path = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)
#######
# Windows #####
#face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
############


cam = cv2.VideoCapture(0)


while True:
    # gets ip of bitdoglab board
    #try:
    #    bitdog_ip = socket.gethostbyname("bitdog.local")
    #except socket.gaierror as e:
    #print("Bitdoglab board not found")

    # Wait until bitdog ip address is received
    bitdog_ip=None
    while( bitdog_ip is None):
        bitdog_ip=send_udp_broadcast(b"RESOLVE bitdog")
    print(bitdog_ip)

    ret, frame = cam.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    dx, dy = 127, 127  # Default if no face

    if len(faces) > 0:
        # Pick the largest face
        x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
        center_x = x + w // 2
        center_y = y + h // 2

        # Normalize positions to 0-100 (example range)
        dx = int(-( ( center_x / frame.shape[1]) * 100-50))
        dy = int( ( center_y  / frame.shape[0]) * 100-50)
        # Show detection
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Send dx, dy as 2-byte values through UDP
        data = struct.pack('bb', dx, dy)
        sock.sendto(data, (bitdog_ip, PORT_XY))  

    cv2.imshow("Face Tracking", frame)
    if cv2.waitKey(1) == 27:  # ESC key
        break

cam.release()
sock.close()
cv2.destroyAllWindows()
