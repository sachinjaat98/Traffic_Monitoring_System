from flask import Flask, render_template, Response
import boto3
import io
import cv2
from time import sleep
import pandas as pd
from threading import Thread
import numpy as np
from process import Process
from datetime import datetime
import pytz

headers = 'Sitename DateTime Cars Trucks Bikes Pedestrians Latitude Longitude'
headers = headers.split(' ')

df = pd.DataFrame(columns = headers)
df.to_csv('stats.csv', index = False)

# Initialize the processing of frames
process = Process().start1()

def write_csv():
    global df
    sleep(5)

    s3 = boto3.client('s3')
    s3.download_file('cam.frames', 'info.txt', 'info.txt')
    f = open("info.txt", "r")
    line = f.read()
    cameraid, zone,lat,longi = line.split(' ')
    tz = pytz.timezone(zone)
    print(cameraid, zone)

    while(True):
        now = datetime.now(tz)
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        p,c,b,t = process.retrieve_stats()
        instance = np.matrix([cameraid,dt_string,c,t,b,p,lat,longi])
        #print(instance)
        df1 = pd.DataFrame(instance, columns=headers)
        df = df.append(df1)
        df.to_csv('stats.csv', index = False)
        #print('csv_updated')
        sleep(10)

def upload_csv():
    s3 = boto3.resource('s3')
    bucket_name = 'cam.frames'
    global df
    sleep(10)
    while True:
        s3.meta.client.upload_file('stats.csv', bucket_name, 'stats.csv')
        #print('csv_uploaded')
        sleep(20)


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


def gen():

    while(True):
        # read the latest processed frame
        frame = process.read1()
        encode_return_code, image_buffer = cv2.imencode('.jpg', frame)
        io_buf = io.BytesIO(image_buffer)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')

@app.route('/video_feed')
def video_feed():

    return Response(
        gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

th1 = Thread(target=write_csv)
th2 = Thread(target=upload_csv)
th1.start()
th2.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000, debug=True, threaded=True)

