import boto3
from time import sleep
import cv2
#from video import VideoStream
import requests
import pytz

"""cameraid = 'camera1'
x = requests.get('http://ip-api.com/json/192.168.1.5')
data = x.json()
zone = data['timezone']
lat = str(data['lat'])
longi = str(data['lon'])
#print(zone)

f = open("info.txt", "w")
f.write(cameraid+' '+zone+' '+lat+' '+longi)
f.close()"""


s3 = boto3.resource('s3')
bucket_name = 'kinesisprojectbucket'
key_path = 'image.jpg'
s3.meta.client.upload_file('Scene_Text_Detection/info.txt', bucket_name, 'info.txt')

# Initialize frame rate calculation
#videostream = VideoStream(framerate=30).start()
cap = cv2.VideoCapture(0)
print('Server Started...')
sleep(1)

while True:  # send images as stream until Ctrl-C

    frame = cap.read()
    img = cv2.imencode('.jpg',frame)[1].tobytes()
    s3.Object(bucket_name,key_path).put(Body=img,ContentType='image/JPG')
    #print('uploaded')



