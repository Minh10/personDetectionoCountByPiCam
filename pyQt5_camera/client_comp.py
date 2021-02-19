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
q =90 #quality

count = 0
while ret:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #gray = cv2.GaussianBlur(gray, (21,21), 0) #filter salt & peper noise
    if count == 0:
        fref = gray #reference frame
    else:
        fcur = gray #current frame
        frameDelta = cv2.absdiff(fref, fcur)
        ret, thres = cv2.threshold(frameDelta, 100, 250, cv2.THRESH_BINARY)
        print(sum(sum(thres)))
        motionThres = abs((gray.size)*0.000001*255) #0.001% of frame
        if sum(sum(thres)) > motionThres:
            print(1)
            q =90
        else:
            print(0)
            q = 30
    count +=1
    fref = gray
    # compress frame
    retval, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY),q])
    
    if retval:
        # convert to byte array
        buffer = buffer.tobytes()
        # get size of the frame
        buffer_size = len(buffer)
        #print(buffer_size)
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
    
    ret, frame = cap.read()

print("done")
