Please unzip before running the code file.

This folder contains 2 major code file
- the edge_test.py run on laptop
- the device_operate.ino running on Arduino UNO3

-------------------------------------------------------------------
Please install the follow dependecies for edge_test.py

opencv 4.7.0.68 
pyserial 3.5

-run the python file which will automatically run the sample image
under the same folder diretory and send the extracted info to the arduino

-before execute, make sure arduino connected to laptop. And the Arduino
IDE (editor) is closed and not using the COM port.

-if error happened, most likely is the wrong COM port selected or no port found.
need to check on which port the arduino connected to.
--------------------------------------------------------------------
device_operate.ino

There is no need to compile and upload to arduino again. the device should
have memory on last upload

This file is just for you to set upp the physical cables with the
corresponding pins and locations of the LED matrix

version python 1.10.11

Install 
conda install -c conda-forge opencv
conda install -c anaconda pyserial
conda install -c anaconda pillow 
conda install -c conda-forge gtts 
conda install -c conda-forge pydub
conda install -c conda-forge ffmpeg

python -u "/Users/williamfisilo/Desktop/Tactilesys/Tactile_backend/edge_test.py"

run this for object detection plan
cd darknet
./darknet detector test cfg/coco.data cfg/yolov3.cfg yolov3.weights /Users/williamfisilo/Downloads/test2/data/temp/camera_capture_0.jpg


//still in progress

simplify the process