import cv2
import socket
import struct
from time import sleep
# IP and port of the BitDogLab plate (replace with actual IP)
UDP_IP = '192.168.18.16'
PORT = 12345

# Setup socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Load OpenCV face detector

# Open CV Pretrained model for faces
# Arch linux #####
#cascade_path = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
#face_cascade = cv2.CascadeClassifier(cascade_path)
#######
# Windows #####
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
############


cam = cv2.VideoCapture(0)

while True:
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
    sock.sendto(data, (UDP_IP, PORT))  

    cv2.imshow("Face Tracking", frame)
    if cv2.waitKey(1) == 27:  # ESC key
        break

cam.release()
sock.close()
cv2.destroyAllWindows()
