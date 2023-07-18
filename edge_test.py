import cv2
import numpy as np
import serial
import serial.tools.list_ports as S
import time
import os
from PIL import Image
import argparse 
import sys
from pathlib import Path
import re

#initialiser
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative



#object detection test
def yolo_test(path):
    # os.chdir('darknet') #change directory
    # os.system('./darknet detector test cfg/coco.data cfg/yolov3.cfg yolov3.weights /Users/williamfisilo/Desktop/Tactilesys/tactile_backend/data/temp/camera_capture_0.jpg')
    
    filename = os.path.basename(path)
    os.chdir('yolov5')
    os.system('python detect.py --weights yolov5s.pt --source ' + path)
    image = Image.open(ROOT/ "results" /filename)
    image.show(image)
    os.remove(ROOT/ "results" /filename)
    os.chdir("..")
    
# def voice_out():
#     os.system('say "There is one person"')

#live camera detection
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

#tactile actuator
def edge_photo (path):
    # width1 = int(input("width:"))
    # height1 =int(input("height:")) custom pixel
    print(path)
    width1 = 100
    height1 = 100
    
    # Read the original image
    img = cv2.imread(path)
    width,height=img.shape[:2]
    # Display original image
    cv2.imshow('Original', img)
    time.sleep(1)
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
    # Close all OpenCV windows
    cv2.destroyAllWindows()
    return edges

#sending signal to tactile
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
        
# user interface (main)
def parseopt():
    #in progress
    parser = argparse.ArgumentParser(description = 'path to image')
    parser.add_argument('-i', '--input', type = str, help = 'input image directory')              
    parser.add_argument('-o', '--output', type = str, help = 'output image directory')
    parser.add_argument('-d', '--detecton', type = bool, help = 'Detection on')
    parser.add_argument('-non', '--live', type = str, default = "yes", help = 'image')
    opts = parser.parse_args()
    return opts

def tactile(path, img):
    # tactile elevation
    port = connect()
    
    try:
        print(port.isOpen())
    except AttributeError:
        print("no port is connected")
    
    #return row and col coordinate of non-zero pixel
    have_pix=pixel_location(img)
    
    #to send over to arduino through port connected
    send_serial(have_pix, port)
    # Close the serial port when done
    port.close()
    
def rembg(path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    newpath = os.path.join(current_dir, "data/temp/(b).jpeg")
    os.system("rembg i " + path + " " + newpath)
    pass
    
def detect_options(path):
    while True:
        newoptions = input('please select an option\n'
                            'a) Object detection and sound output\n'
                            'b) tactile activation\n'   
                            'c) Remove background (beta)\n'
                            'd) return to main menu\n'
                            'e) exit\n')
        
        newoptions = newoptions.lower()
        
        if newoptions == "a":
            #object detection and sound output
            yolo_test(path)
            
        elif newoptions == "b":
            #edge detection
            img = edge_photo(path)
            
            #tactile elevation
            #tactile(path, img)
        elif newoptions == "c":
            #rembg
            rembg(path)
            
        elif newoptions == "d":
            #return to main menu
            os.remove(path)
            print("Back to main menu")
            break

        elif newoptions == "e":
            #exit
            os.remove(path)
            print("exit")
            sys.exit()
            
        else:
            #error
            print("invalid option")
            continue

            
if __name__ == "__main__":
    args = parseopt()
    path = args.input
    
    if path is not None:
        pass
        sys.exit(0)
    
    while True:
        options = input('please enter an option you want to have\n'
                        'a) Live detection\n'
                        'b) put in an image\n'
                        'c) exit the system\n')
        
        options = options.lower()
        #path input
        if options == "a":
            #live image taking
            save_frame_camera_key(0, "data/temp", 'camera_capture')
            current_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(current_dir, "data/temp/camera_capture_0.jpg")
            detect_options(path)
            
        
       # Image input
        elif options == "b":
            while True:
                # Ask for the image name
                image_name = input("Enter the name of the image (with extension): ")

                # Check if correct path
                folder_path = "data/temp"
                image_extensions_pattern = re.compile(r".*\.(jpg|jpeg|png|gif|bmp)$", re.IGNORECASE)

                # Get list of image files in the directory
                image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and image_extensions_pattern.match(f)]

                # Check if the image exists in the directory
                if image_name in image_files:
                    print(f"{image_name} is a valid image.")
                    break
                else:
                    print(f"{image_name} is not found in the directory. Please try again.")
                            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            imgpath = os.path.join(current_dir, "data/temp", image_name)
            detect_options(imgpath)
                
        elif options == "c":
            #exit the system
            print("exit")
            sys.exit(0)
        
        else: 
            continue
                
    #exit program   
    sys.exit(0)
