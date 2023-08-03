import numpy as np
import cv2
import serial
import serial.tools.list_ports as S
import time
import os
from PIL import Image
import argparse
import sys
from pathlib import Path
import re
from paddleocr import PaddleOCR,draw_ocr
import os 
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
midas_path = os.path.join(current_dir, "midas")
sys.path.append(midas_path)

import run

class TactileSystem:
    def __init__(self):
        self.FILE = Path(__file__).resolve()
        self.ROOT = self.FILE.parents[0]
        if str(self.ROOT) not in sys.path:
            sys.path.append(str(self.ROOT))
        self.ROOT = Path(os.path.relpath(self.ROOT, Path.cwd()))
        self.width2 =  100
        self.height2 = 100

    def yolo_test(self, path):
        filename = os.path.basename(path)
        os.chdir('yolov5')
        os.system(f'python detect.py --weights yolov5s.pt --source {path}')
        image = Image.open(self.ROOT / "results" / filename)
        image.show(image)
        os.remove(self.ROOT / "results" / filename)
        os.chdir("..")

    def save_frame_camera_key(self, device_num, dir_path, basename, ext='jpg', delay=1, window_name='frame'):
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
                cv2.imwrite(f'{base_path}_{n}.{ext}', frame)
                break

        cv2.destroyWindow(window_name)

    def edge_photo(self, path, width1, height1):
        img = cv2.imread(path)
        width, height = img.shape[:2]
        cv2.imshow('Original', img)
        cv2.waitKey(1)
        img = cv2.resize(img, (width1, height1), interpolation=cv2.INTER_AREA)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(image=img, threshold1=100, threshold2=200)
        print("the shape of processed picture is {}".format(edges.shape))
        to_show = cv2.resize(edges, (width, height), interpolation=cv2.INTER_NEAREST)
        cv2.imshow('Canny Edge Detection', to_show)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return edges

    def pixel_location(self, img):
        have_pixel = np.where(img > 0)
        print(have_pixel)
        return have_pixel

    def wait_response(self, port):
        while True:
            if port.read().decode() == '1':
                break

    def send_serial(self, have_pix, port):
        port.write("s".encode('ascii'))
        length = len(have_pix[0])
        to_send = ""
        self.wait_response(port)
        print("now sending pixel info")
        for i in range(length):
            row = have_pix[0][i]
            col = have_pix[1][i]

            to_send += 'r' + str(row) + 'c' + str(col)
            if len(to_send) >= 32:
                port.write(to_send.encode('ascii'))
                to_send = ""
                self.wait_response(port)
        print(to_send)
        port.write(to_send.encode('ascii'))
        self.wait_response(port)
        port.close()

    def connect(self):
        port_list = sorted(S.comports())
        name = ""
        if len(port_list) > 0:
            name = port_list[0][0]
        try:
            port = serial.Serial(name, 9600)
            print("{}is connected successfully".format(name))
            time.sleep(2)
            return port
        except:
            print(" error occurred during connection set up")
            return None

    def tactile(self, path, img):
        port = self.connect()

        try:
            print(port.isOpen())
        except AttributeError:
            print("no port is connected")

        have_pix = self.pixel_location(img)
        self.send_serial(have_pix, port)
        port.close()

    def rembg(self, path):
        newpath = os.path.basename(path)
        name, extension = os.path.splitext(newpath)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        imgpath = os.path.join(current_dir, "data/temp", name + "_bg" + extension)
        os.system("rembg i " + path + " " + imgpath)
        return imgpath

    def text_detect(self, path):
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        result = ocr.ocr(path, cls=True)
        for idx in range(len(result[0])):
            print(result[0][idx][1][0])
            os.system('say -v Samantha ' + result[0][idx][1][0])
            
    def clear_folder(self):
        directory = self.ROOT / 'data/temp'
        for image in os.listdir(directory):
            if image is not None:
                file_img = os.path.join(directory, image)
                os.remove(file_img)
            
    def detect_options(self, path, width2, height2):
        while True:
            newoptions = input('please select an option\n'
                               'a) Object detection and sound output\n'
                               'b) tactile activation\n'
                               'c) Remove background\n'
                               'd) Depth detection\n'
                               'e) return to main menu\n'
                               'f) exit\n')

            newoptions = newoptions.lower()

            if newoptions == "a":
                self.yolo_test(path)
                self.text_detect(path)

            elif newoptions == "b":
                img = self.edge_photo(path, width2, height2)
                #tactile(path, img)
                # port=connect()
                # try:
                #     print(port.isOpen())

                # except AttributeError:
                #     print("no port is connected")
                
                # #return row and col coordinate of non-zero pixel
                # have_pix=pixel_location(img)
                # #to send over to arduino through port connected
                # send_serial(have_pix,port)

            elif newoptions == "c":
                path = self.rembg(path)
            
            elif newoptions == "d":
                depth_tac = run.run("data/temp", "data/temp", "midas/weights/dpt_swin2_large_384.pt", "dpt_swin2_large_384", width2, height2)
                print(depth_tac)
                
            elif newoptions == "e":
                print("Back to main menu")
                break

            elif newoptions == "f":
                print("exit")
                self.clear_folder()
                sys.exit()

            else:
                print("invalid option")
                continue

    def parseopt(self):
        parser = argparse.ArgumentParser(description='path to image')
        parser.add_argument('-i', '--input', type=str, help='input image directory')
        parser.add_argument('-o', '--output', type=str, help='output image directory')
        parser.add_argument('-d', '--detection', type=str, help='choose between "image" or "camera" for object detection')
        args = parser.parse_args()

        if not args.detection and not args.output and not args.input:
            return "a"

        if not args.detection:
            print("please specify if you want to use the software live or not using -d or --detection argument")
            return "b"

        if not args.input and args.detection == "image":
            print("Please provide input image directory using -i or --input argument")
            return "b"

        return args

    def run(self):
        args = self.parseopt()

        if args == "b": 
            #invalid option
            directory = "data/temp"
            sys.exit(0)

        elif args == "a":
            #normal route
            while True:
                options = input('please enter an option you want to have\n'
                                'a) Live detection\n'
                                'b) Put in an image\n'
                                'c) Exit the system\n')

                options = options.lower()

                if options == "a":
                    self.save_frame_camera_key(0, "data/temp", 'camera_capture')
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    path = os.path.join(current_dir, "data/temp/camera_capture_0.jpg")
                    self.detect_options(path, self.width2, self.height2)

                elif options == "b":
                    while True:
                        image_name = input("Enter the name of the image (with extension): ")
                        folder_path = "data/temp"
                        image_extensions_pattern = re.compile(r".*\.(jpg|jpeg|png|gif|bmp)$", re.IGNORECASE)
                        image_files = [f for f in os.listdir(folder_path) if
                                       os.path.isfile(os.path.join(folder_path, f)) and image_extensions_pattern.match(f)]

                        if image_name in image_files:
                            print(f"{image_name} is a valid image.")
                            break
                        else:
                            print(f"{image_name} is not found in the directory. Please try again.")

                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    imgpath = os.path.join(current_dir, "data/temp", image_name)
                    self.detect_options(imgpath, self.width2, self.height2)

                elif options == "c":
                    print("Exit")
                    self.clear_folder()
                    sys.exit(0)
                else:
                    continue

        else:
            #args path, short cut
            if args.detection == "live":
                self.save_frame_camera_key(0, "data/temp", 'camera_capture')
                current_dir = os.path.dirname(os.path.abspath(__file__))
                path = os.path.join(current_dir, "data/temp/camera_capture_0.jpg")
                self.yolo_test(path)
                self.text_detect(path)

            elif args.detection == "image":
                current_dir = os.path.dirname(os.path.abspath(__file__))
                path = os.path.join(current_dir, "data/temp/" + args.input)
                self.yolo_test(path)
                self.text_detect(path)
            else:
                print("please put in the proper parameters")

def main():
    system = TactileSystem()
    system.run()

if __name__ == "__main__":
    main()
