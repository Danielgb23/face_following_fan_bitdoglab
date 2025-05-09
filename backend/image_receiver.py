import socket
import numpy as np
import cv2

# UDP config
UDP_IP = "0.0.0.0"
UDP_PORT = 12346

sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv.bind((UDP_IP, UDP_PORT))

def receive_frame():
    # First, get the image size (sent as 4 bytes, little endian)
    size_data, _ = sock_recv.recvfrom(4)
    if len(size_data) != 4:
        return None
    img_size = int.from_bytes(size_data, 'little')

    # Receive the full image data
    buffer = bytearray()
    while len(buffer) < img_size:
        try:
            part, _ = sock_recv.recvfrom(2048)
            buffer.extend(part)
        except socket.timeout:
            break
    # Decode JPEG image
    img_array = np.frombuffer(buffer, dtype=np.uint8)

    # incomplete image
    if len(img_array) != img_size:
        print("corrupted data")
        return None

    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return frame

while True:
    frame = receive_frame()
    if frame is not None:
        cv2.imshow("ESP32-CAM Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

sock_recv.close()
cv2.destroyAllWindows()
