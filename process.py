import os
import cv2
import numpy as np
import sys
from threading import Thread
from time import sleep
import boto3
import importlib.util

class Process:
    
    """Module for object detection and return frames from a threaded function"""
    def __init__(self):
        # Initialize the PiCamera and the camera image stream
        self.s3 = boto3.client('s3')
        self.s3.download_file('pi.frames', 'image.jpg', 'image.jpg')
        self.frame1 = cv2.imread('image.jpg')
        
        self.person_count = 0
        self.trucks_count = 0
        self.bikes_count = 0
        self.cars_count = 0
    def start1(self):
        # Start the thread that reads frames from the video stream
        Thread(target=self.update1,args=()).start()
        #print('3')
        return self

    def update1(self):
        MODEL_NAME = 'sample'
        GRAPH_NAME = 'detect2.tflite'
        LABELMAP_NAME = 'labelmap2.txt'
        min_conf_threshold = 0.5
        resW, resH = (1280,720)
        imW, imH = int(resW), int(resH)


        # Import TensorFlow libraries
        # If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
        pkg = importlib.util.find_spec('tflite_runtime')
        if pkg:
            from tflite_runtime.interpreter import Interpreter
        else:
            from tensorflow.lite.python.interpreter import Interpreter

        # Get path to current working directory
        CWD_PATH = os.getcwd()

        # Path to .tflite file, which contains the model that is used for object detection
        PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

        # Path to label map file
        PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

        # Load the label map
        with open(PATH_TO_LABELS, 'r') as f:
            labels = [line.strip() for line in f.readlines()]

        # Have to do a weird fix for label map if using the COCO "starter model" from
        # https://www.tensorflow.org/lite/models/object_detection/overview
        # First label is '???', which has to be removed.
        if labels[0] == '???':
            del(labels[0])

        # Load the Tensorflow Lite model.
        interpreter = Interpreter(model_path=PATH_TO_CKPT)
        interpreter.allocate_tensors()

        # Get model details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]
        floating_model = (input_details[0]['dtype'] == np.float32)

        input_mean = 127.5
        input_std = 127.5
        # Initialize frame rate calculation
        frame_rate_calc = 1
        freq = cv2.getTickFrequency()


        while True:
            person_count=0
            cars_count=0
            trucks_count=0
            bikes_count=0

            t1 = cv2.getTickCount()
            # Otherwise, grab the next frame from the stream
            self.s3.download_file('pi.frames', 'image.jpg', 'image.jpg')
            frame = cv2.imread('image.jpg')
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)
            # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

            # Perform the actual detection by running the model with the image as input
            interpreter.set_tensor(input_details[0]['index'],input_data)
            interpreter.invoke()

            # Retrieve detection results
            boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
            classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
            scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
            #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

            # Loop over all detections and draw detection box if confidence is above minimum threshold
            for i in range(len(scores)):
                if ((int(classes[i])<8) and (scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

                    # Get bounding box coordinates and draw box
                    # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                    ymin = int(max(1,(boxes[i][0] * imH)))
                    xmin = int(max(1,(boxes[i][1] * imW)))
                    ymax = int(min(imH,(boxes[i][2] * imH)))
                    xmax = int(min(imW,(boxes[i][3] * imW)))

                    cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                    # Draw label
                    object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                    if object_name=='person':
                        person_count+=1
                    if object_name=='car':
                        cars_count+=1

                    label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                    label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                    cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                    cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

            # Draw framerate in corner of frame
            cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
            cv2.putText(frame, 'person: '+str(person_count), (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, 'cars: '+str(cars_count), (600, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, 'bikes: '+str(bikes_count), (400, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, 'trucks: '+str(trucks_count), (600, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            # All the results have been drawn on the frame, so it's time to display it.
            #cv2.imshow('Object detector', frame)


            # Calculate framerate
            t2 = cv2.getTickCount()
            time1 = (t2-t1)/freq
            frame_rate_calc= 1/time1
            self.frame1 = frame
            self.person_count = person_count
            self.cars_count = cars_count
            self.bikes_count = bikes_count
            self.trucks_count = trucks_count
            
    def read1(self):
        # Return the most recent frame
        return self.frame1
    
    def retrieve_stats(self):
        #print('csv')
        return (self.person_count,self.cars_count,self.bikes_count,self.trucks_count)

