import cv2
import socket
import math
import pickle
import sys

max_length = 65000
host = '127.0.0.1'
port = 12008

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print(frame.shape)
while ret:
    # compress frame
    retval, buffer = cv2.imencode(".jpg", frame)
    buffer = cv2.resize(buffer, (170,140))
    #buffer = frame
    if retval:
        # convert to byte array
        buffer = buffer.tobytes()
        # get size of the frame
        buffer_size = len(buffer)

        print(buffer_size)
        num_of_packs = 1
        if buffer_size > max_length:
            num_of_packs = math.ceil(buffer_size/max_length)

        frame_info = {"packs":num_of_packs}

        # send the number of packs to be expected
        sock.sendto(pickle.dumps(frame_info), (host, port))
        
        left = 0
        right = max_length

        for i in range(num_of_packs):
            # truncate data to send
            data = buffer[left:right]
            left = right
            right += max_length

            # send the frames accordingly
            sock.sendto(data, (host, port))
	
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    ret, frame = cap.read()
cap.release()
print("done")
