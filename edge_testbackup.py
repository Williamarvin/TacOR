import cv2
import numpy as np
import serial
import serial.tools.list_ports as S
import time
import os
import subprocess
from PIL import Image
import string
import argparse 
import sys
from pathlib import Path

#initialiser
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

#input 
parser = argparse.ArgumentParser(description = 'path to image')
parser.add_argument('-i', '--input', type = str, help = 'input image directory')        #in progress
parser.add_argument('-o', '--output', type = str, help = 'output image directory')
parser.add_argument('-d', '--detecton', type = bool, help = 'Detection on')
parser.add_argument('-non', '--live', type = str, default = "yes", help = 'image')
args = parser.parse_args()

def yolo_test():
    # os.chdir('darknet') #change directory
    # os.system('./darknet detector test cfg/coco.data cfg/yolov3.cfg yolov3.weights /Users/williamfisilo/Desktop/Tactilesys/tactile_backend/data/temp/camera_capture_0.jpg')
    filename = os.path.basename(args.input)
    os.chdir('yolov5')
    os.system('python detect.py --weights yolov5s.pt --source ' + args.input)
    image = Image.open(ROOT/ "results" /filename)
    image.show(image)
    os.remove(ROOT/ "results" /filename)
    
    
# def voice_out():
#     os.system('say "There is one person"')

def save_frame_camera_key(device_num, dir_path, basename, ext='jpg', delay=1, window_name='frame'):
    cap = cv2.VideoCapture(device_num)

    if not cap.isOpened():
        return

    os.makedirs(dir_path, exist_ok=True)
    base_path = os.path.join(dir_path, basename)
    n = 0
    while True:
        ret, frame = cap.read()
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(delay) & 0xFF
        if key == ord('c'):
            cv2.imwrite('{}_{}.{}'.format(base_path, n, ext), frame)
            break

    cv2.destroyWindow(window_name)


def edge_photo (path):
    # width1 = int(input("width:"))
    # height1 =int(input("height:")) custom pixel
    width1 = 100
    height1 = 100
    
    # Read the original image
    img = cv2.imread(path)
    width,height=img.shape[:2]
    # Display original image
    cv2.imshow('Original', img)
    cv2.waitKey(0)
    img = cv2.resize(img, (width1, height1), interpolation=cv2.INTER_AREA)
    # Convert to graycsale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur the image for better edge detection
    #img = cv2.GaussianBlur(img, (3, 3), 0)


    # Canny Edge Detection
    edges = cv2.Canny(image=img, threshold1=100, threshold2=200)  # Canny Edge Detection
    print("the shape of processed picture is {}".format(edges.shape))
    # Display Canny Edge Detection Image
    to_show= cv2.resize(edges,(width,height), interpolation=cv2.INTER_NEAREST)
    cv2.imshow('Canny Edge Detection',to_show)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return edges

def pixel_location(img):
    #to extract coordinate of array with non-zero pixels
    have_pixel=np.where(img>0)
    print(have_pixel)
    return have_pixel

def wait_response(port):
    while True:
        if (port.read().decode() == '1'):
            break

def send_serial(have_pix,port):
    port.write("s".encode('ascii'))
    length= len(have_pix[0])
    to_send = ""
    wait_response(port)
    print("now sending pixel info")
    for i in range(length):
        row= have_pix[0][i]
        col=have_pix[1][i]

        to_send+='r'+str(row)+'c'+str(col)
        if len(to_send)>=32: #to ensure the byte buffer of receiver still was not overloaded
            port.write(to_send.encode('ascii'))
            to_send=""
            wait_response(port)
    print(to_send)
    port.write(to_send.encode('ascii'))
    wait_response(port)
    port.close()

def connect():
    port_list = sorted(S.comports())
    name=""
    if len(port_list) > 0:
        #name = port_list[2][0]
        name = port_list[0][0]
    try:
        port = serial.Serial(name, 9600)
        print("{}is connected successfully".format(name))
        time.sleep(2)
        return port
    except:
        print(" error occured during connection set up")

if __name__ =="__main__":
    path = args.input
    #live camera
    
    if args.live == "yes":
        save_frame_camera_key(0, 'data/temp', 'camera_capture')
    
    #processed photo and get the edges of the photo
    img = edge_photo(path)
    print(img)
    
    #object detection
    yolo_test()
    
    #delete image
    os.remove(path)
    
    #exit program
    sys.exit(0)
    
#to initiate connection with arduino
    # port=connect()
    # try:
    #     print(port.isOpen())

    # except AttributeError:
    #     print("no port is connected")
    # #return row and col coordinate of non-zero pixel
    # have_pix=pixel_location(img)
    # #to send over to arduino through port connected
    # send_serial(have_pix,port)
    
    

