# Traffic_Monitoring_System
traffic monitoring system utilizing computer vision AI. This system accurately identifies vehicle types, captures their speed, and extracts vital data to optimize traffic management on highways, aiding in efficient traffic flow control;
Vehicle detection using CCTV and online Streaming


This project is about detecting vehicles on the road using an IP CCTV camera. The raspberry Pi is used as a processing unit to capture frames from CCTV and upload them to AWS S3 cloud bucket  and AWS EC2 is used to process frames and  apply object detection using a Tflite model.
The streaming is done by flask on the public ip provided by the cluster.

## Getting Started
You should have your Raspbian software installed on the Raspberry pi with python 3.6+ Make a new working directory for this project in which code files and virtual environment will be present. Here it is named tflite.
In EC2 cluster python 3.6+ is included with the Ubuntu cluster.

## 1.Work to be done on AWS
### 1.1 Creating a virtual environment
Install the virtualenv library
sudo pip3 install virtualenv

### create a environment named tflite-env inside the folder:
cd tflite
python3 -m venv tflite-env

### To activate tflite-env:
source tflite-env/bin/activate
To deactivate env anytime:
deactivate

1.2 Installing Required libraries:
1.2.1 OPENCV
Get packages required for OpenCV
sudo apt-get -y install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get -y install libxvidcore-dev libx264-dev
sudo apt-get -y install qt4-dev-tools libatlas-base-dev

Installing OpenCV:

pip3 install opencv-python

1.2.2 Tensorflow lite:

Get packages required for TensorFlow Using the tflite_runtime packages available at
https://www.tensorflow.org/lite/guide/python
pip3 install tensorflow

For the installation of tflite runtime on pi
if [ python version == "3.7" ], then
pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl
if [ python version == "3.6" ], then
pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp36-cp36m-linux_armv7l.whl

1.2.3 FLASK

pip3 install Flask

1.2.4 Boto3
pip3 install boto3

1.2.5 MYSQL
pip3 install mysql
pip3 install sqlalchemy

1.2.6 Some other libraries needed:
pip3 install numpy
pip3 install pandas
pip3 install pytz

1.3 Installing AWS CLI on EC2:
Version -2 for linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

1.4 Configure AWS CLI

Configure the default AWS CLI

aws configure
AWS Access Key ID [None]: XXXXXXXXXXXXXXXX
AWS Secret Access Key [None]: XXXXXXXXXXXXXXXXXXXXXXXXX
Default region name [None]:  ap-south-1b
Default output format [None]: json

“””2.5 Pretrained models”””
Download the ssd_mobilenet_v1 model and unzip it (on pi)
wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip

unzip coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip



2.Work to be done on Raspberry Pi
2.1 Creating a folder named Iot in home directory
2.2 Libraries needed :- boto3, pytz , opencv,  numpy ,  pandas

2.3 Installing AWS CLI on raspberry pi:
pip3 install awscli --upgrade --user

Add AWS CLI executable to your Command Line Path
export PATH=/home/pi/.local/bin:$PATH



2.4  Configure AWS CLI

Configure the default AWS CLI

aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json



3.Description
3.1 Pretrained model
The model used in this approach is ssd_inception_v2 tflite model. This model is not quantized.
3.2 Files
process.py - a class script containing threaded functions to process frames from the s3 bucket and return the latest processed frame
botoclient.py - flask script to open server to an open port. Contains functions to render the latest processed frames, to append csv file and to upload into s3 bucket
rds_upload.py - script to upload the csv data into AWS-rds MySQL database
template/index.html - a HTML file to render the frames
sample - folder containing models and labels

3.3 Programs to be run on AWS EC2:
1.botoclient.py
2.rds_upload.py
3.4 Programs to be run on Pi:
Botoserver.py

4. Auto start Python script with Pi boot:

If you need access to elements from the X Window System (e.g. you are making a graphical dashboard or game), then you will need to wait for the X server to finish initializing before running your code. One way to accomplish this is to use the autostart system.
4.1 Create a .desktop File
You do not need root-level access to modify your profile's (user's) autostart and .desktop files. In fact, it is recommended that you do not use sudo, as you may affect the permissions of the file (e.g. the file would be owned by root) and make them unable to be executed by autostart (which has user-level permissions).
Open a terminal, and execute the following commands to create an autostart directory (if one does not already exist) and edit a .desktop file

mkdir /home/pi/.config/autostart
nano /home/pi/.config/autostart/script.desktop

4.2 Copy in the following text into the script.desktop file. Feel free to change the Name and Exec variables to your particular application.

[Desktop Entry]
Type=Application
Name= Iot
Exec=/usr/bin/python3   /home/pi/python_script.py

Note: since our program needs internet connection , so make sure you have turned on network on boot option in raspberry pi configuration settings using
sudo raspi-config command
Save and exit with ctrl + x, followed by y when prompted to save, and then enter. Reboot with:
sudo reboot

4.3 How to Stop Your Program
If your program is running in the background, there might be no obvious way of halting it. You can always delete your .desktop files and restart, but that might take a while. A better option might be to kill the process associated with your program. In a terminal, enter the following:
sudo ps -ax | grep python

ps -ax tells Linux to list out all the currently processes. We send that output to grep, which allows us to search for keywords. Here, we're looking for python, but feel free to change it to the name of your program. Find the process ID (PID) number to the left of the listed process, and use the kill command to terminate that process:
sudo kill <PID>


5.TMUX session

5.1  sudo apt-get install tmux

5.2 tmux new -s “session name”

5.3 To exit seesion:  exit
5.4 to restore session : tmux  a -t  “sesion name”


