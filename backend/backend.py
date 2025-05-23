import cv2
import socket
import struct
import numpy as np
import threading
import mediapipe as mp
import time

# Mediapipe face detector
mp_face = mp.solutions.face_detection
detector = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)
def get_bigger_face(frame):

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = detector.process(rgb)

    hf, wf, _ = frame.shape

    if result.detections:
        # Find the detection with the largest bounding box area
        largest = max(result.detections, key=lambda d: (
            d.location_data.relative_bounding_box.width *
            d.location_data.relative_bounding_box.height
        ))


        # Get bounding box and convert to pixel coordinates
        bbox = largest.location_data.relative_bounding_box
        x = int(bbox.xmin * wf)
        y = int(bbox.ymin * hf)
        w = int(bbox.width * wf)
        h = int(bbox.height * hf)
        return x, y, w, h
    return None

# ESP32-CAM UDP config
# Create a socket to connect to the ESP32 camera
UDP_IP = "0.0.0.0"
UDP_PORT = 12346 #Selected port specificaly for reciving data packages
sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv.bind((UDP_IP, UDP_PORT))
sock_recv.settimeout(0.06)  # Optional: avoid blocking forever

# Receives a frame from the esp32-cam module
def receive_frame():
    # First, get the image size (sent as 4 bytes, little endian)
    try:
        size_data, _ = sock_recv.recvfrom(4)
    except socket.timeout:
            return None
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
            return None

    # Decode JPEG image
    img_array = np.frombuffer(buffer, dtype=np.uint8)

    # Verify if it is an incomplete image 
    if len(img_array) != img_size:
        #print("corrupted data")
        return None

    #Codify a numpy array as an image
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return frame


# udp broadcast for the mock dns server
# The backend requests the BitDogLab IP from the DNS 
def send_udp_broadcast(message ):
    # send a broadcast with the message
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(message, ("255.255.255.255", 12347))
    sock.settimeout(1)  # Optional: avoid blocking forever
    
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


# bitdog position data socket
# This sends the data containing the face position to BitDogLab's IP adress
sock_xy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
stop=False
def get_bitdog_ip():
    global timer
    global bitdog_ip

    bitdog_ip=None

    while( bitdog_ip is None):
        bitdog_ip=send_udp_broadcast(b"RESOLVE bitdog")
    if bitdog_ip == "NOT_FOUND":
        bitdog_ip=None

    if not stop:
        # Timer to periodically update bitdog ip address
        timer=threading.Timer( 10,get_bitdog_ip )
        timer.start()
    # print("bitdog ip", bitdog_ip)

# Wait until bitdog ip address is received
get_bitdog_ip()


while True:
    try:
        frame = receive_frame()
        if frame is not None: # If it receives a frame, the face recognition is executed
            # gets the bigger face through the face detector
            face = get_bigger_face(frame) 

            if face is not None:
                x, y, w, h = face
                # calculates the face center point
                center_x = x + w // 2
                center_y = y + h // 2
        
                # Normalize positions to 0-100 (example range)
                dx = int(-( ( center_x / frame.shape[1]) * 100-50))
                dy = int( ( center_y  / frame.shape[0]) * 100-50)
                # Show detection
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                #print(dx,dy)    
                
                # Send dx, dy as 2-byte values through UDP
                data = struct.pack('bb', dx, dy)
                # Setup socket connection UDP to send xy to bitdog
                if bitdog_ip is not None:
                    #  Sends the face center coordinates to BitDogLab's IP through port 12345
                    sock_xy.sendto(data, (bitdog_ip, 12345))  

                time.sleep(0.15)

            # Show square indicating recognized face
            cv2.imshow("Face Tracking", frame)
            # sleep to not overload network
        if cv2.waitKey(1) == 27:  # ESC key
            break
        
    except KeyboardInterrupt as ex:
        break


# Closes the script
stop=True # interrupt timer cycle
timer.cancel() # cancel timer
sock_recv.close()
sock_xy.close()
cv2.destroyAllWindows()
