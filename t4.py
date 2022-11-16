

#import packages
import sys, os
import serial
import string
import numpy as np
import argparse
import cv2
import time
import picamera
import picamera.array
from datetime import datetime
from datetime import time
from datetime import timedelta
from PIL import Image
from sys import exit
import subprocess
import requests
import json
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response, send_from_directory, url_for
import threading
# API
import logging.config
from flask import Flask, Blueprint

import sqlalchemy
from sqlalchemy.sql import text
from sqlalchemy import create_engine
#from sqlalchemy import *

# Add the T4 Folder path to the sys.path list for the dir references to work
sys.path.append(os.path.abspath(".."))

# DATA API STUFF
from T4 import settings
from T4.api import api
from T4.api.categories import ns as log_categories_namespace
from T4.api.posts import ns as log_posts_namespace
from T4.database import db

app = Flask(__name__)
logging.config.fileConfig('logging.conf')
log = logging.getLogger(__name__)

def configure_app(flask_app):
    # flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SERVER_HOST'] = settings.FLASK_SERVER_HOST
    flask_app.config['SERVER_PORT'] = settings.FLASK_SERVER_PORT
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP




face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

hog = cv2.HOGDescriptor()
hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector() )

#and define global variables
frame = None
viddyframe = None
roiPts = []
inputMode = False
Width = 320
Height = 240
wl = Width*4.5/10
wr = Width*5.5/10
ht = Height*4.5/10
hb = Height*5.5/10
targetBox = np.array([[wl,ht], [wr,ht], [wr,hb], [wl,hb]])

# TB check these if really neede here
cnt = 0    #count for new roiBox from kalmanfilter 
centerX = 0
centerY = 0
toggle = True #toggle for imshow
flag = True #False #flag for moving

# Camera setup
camera = picamera.PiCamera()
stream = picamera.array.PiRGBArray(camera)
camera.resolution = (Width,Height) #set resolution
camerainit= '"Camera Initialized"'
subprocess.call('espeak '+camerainit, shell=True)

#GPIO Setup
GPIO.setmode(GPIO.BCM)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   23 : {'name' : 'GPIO 23', 'type': GPIO.OUT , 'state' : GPIO.LOW, 'pull' : GPIO.PUD_DOWN},
   24 : {'name' : 'GPIO 24', 'type': GPIO.OUT , 'state' : GPIO.LOW, 'pull' : GPIO.PUD_DOWN}
   }
#GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# Set each pin as an output and make it low:
for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)

# T4 INIT / Database
welcome = '"Welcome to T,4"'
subprocess.call('espeak '+welcome, shell=True)


#def run(stmt):
#    rs = stmt.execute()
#    for row in rs:
#        print row
#s = select([users, emails])
#run(s)

#conn= engine.connect()
#with engine.connect() as conn:
#    conn.execute(log.insert(),title="T4-Taz started", body = "",category_id = 1, pub_date = datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"))
#engine.execute(table_contacts.insert(), email='joe@something.com', cellnumber='267534320')

#i = posts.insert({'title':'T4-Taz started', 'body':'my body','category_id' : 1})
#i.execute()

def sqlite_insert(conn, table, row):
    cols = ', '.join('"{}"'.format(col) for col in row.keys())
    vals = ', '.join(':{}'.format(col) for col in row.keys())
    sql = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(table, cols, vals)
    conn.cursor().execute(sql, row)
    conn.commit()



#sqlite_insert(conn, 'posts', {
#        'title':'T4-Taz started', 
#        'body':'my body',
#        'category_id' : 1, 
#        #'pub_date' : datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
#  })

# example usage
#T4Status("face detected", 1, "Tom Brown").to_json()
#T4Status.from_json(T4Status("tbrown", "Tom Brown").to_json()).to_json()
#class T4Status(object):
#    def __init__(self, title, body, category_id, pub_date, *args, **kwargs):
#        self.name = name
#        self.username = username
#        self.title = title
#        self.body = body
#        self.category_id = category_id
#        self.pub_date = pub_date

#    def to_json(self):
#        return json.dumps(self.__dict__)

#    @classmethod
#    def from_json(cls, json_str):
#        json_dict = json.loads(json_str)
#        return cls(**json_dict)

# SERIAL SETUP
ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=9600,
    parity=serial.PARITY_ODD, # Optional
    stopbits=serial.STOPBITS_ONE, # Optional
    bytesize=serial.EIGHTBITS # Optional
)
# Check if Serial is Open, close and re-open (to avoid exception)
if ser.isOpen():
    ser.close()
ser.open()


class CenterInfo(object):
        def __init__(self): #Init center information

                self.x, self.y = -1, -1

        def __str__(self): #for print center information

                return '%4d %4d' % (self.x, self.y)


#Select RoiBox points from mouse click
# ### Do this programmatically / the orchestrator
def selectROI(event, x, y, flags, param):
    global frame, roiPts, inputMode

    if inputMode and event == cv2.EVENT_LBUTTONDOWN and len(roiPts) < 4:
        roiPts.append((x,y))
        cv2.circle(frame,(x,y),4,(0,255,0),2)
        
        
def SendMotor(x,y):
    if x / 10 == 0:
        tempCenterX = '00' + str(x)
    elif x / 100 == 0:
        tempCenterX = '0' + str(x)
    else:
        tempCenterX = str(x)                    
    if y / 10 == 0:
        tempCenterY = '00' + str(y)
    elif y / 100 == 0:
        tempCenterY = '0' + str(y)
    else:
        tempCenterY = str(y)
    centerData = str(int(flag)) + tempCenterX + tempCenterY                 
    #print centerData
    # TODO check the time and flag to send information to Arduino. (Data is not sent until delta seconds)
    if datetime.now() > time3 + delta : #if 1 == 1:   #
        if serial_flag_bit == 1:    # if 1 == 1: #
            ser.write('%s' %centerData)

# STATUS LOG FUNCION
# category_id Category
#       4        System
#       5        Motion
#       6        Body Detected
#       7        Face Detected
def postLog(json_data):
    headers = {'Content-type': 'application/json'}
    response = requests.post('http://localhost:5000/api/log/posts/', data=json_data, headers=headers)
    print(response)

def T4action():
    #If status changed for a duration of time.
    #0. Voice activate system
    #1. Motion -> follow object
    #- 2. Detect body (HOG) -> track done by opencv loop 
    #- - 3. Detect face-> Make picture & send (stacked) -> go to Aim
    #- - - 4. Aim -> laser led on + sound alarm + audible warning
    #- - - - 5. Shoot -> Laser led blink + gun sounds + (voice-shoot)
	# - - - - WHEN TO LOG!!
    #0. Voice de-activate
    #Python if elif

    # Write bootup status to log
    data = {"body": "Started T4 server", "category": "System", "title": "T4-Taz_001 started","category_id": 4} #{"data" : "24.3"}
    postLog(json.dumps(data))
    

#    var = 100
#    if var == 200:
#       print "1 - Got a true expression value"
#       print var
#    elif var == 150:
#       print "2 - Got a true expression value"
#       print var
#    elif var == 100:
#       print "3 - Got a true expression value"
#       print var
#    else:
#       print "4 - Got a false expression value"
#       print var
#
#    print "Good bye!"




def T4main():

    global frame, roiPts, inputMode, roiBoxWidth, roiBoxHeight, time3, delta, serial_flag_bit
    cnt = 0    #count for new roiBox from kalmanfilter 
    
    # Tracking fill follow eithe the biggest Hog or Face
    bigHog=[0,0,0,0] 
    bigFace=[0,0,0,0]
    stepperX = 0
    stepperY = 0
    
    centerX = 0
    centerY = 0
    toggle = True #toggle for imshow
    flag = True #False #flag for moving

    kalman2d = cv2.KalmanFilter() #Kalman2D() #Create new Kalman filter and initailize

    # TO DO: Receive initial position from settings or Orchestrator
    # cv2.setMouseCallback("frame",selectROI) #mouseCallback RECEIVE FROM ORCHESTRATOR

    termination = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,10,3) #camshift termination condition

    roiBox = None
    
    time2 = datetime.now() #<<<check time>>>
    time3 = datetime.now() 
    serial_flag_bit = 1 #Sending data flag
    delta = timedelta(seconds = 1) #sleep time for init RoiBox
    
    # ### TODo: once per new detection???
    # detection= '"Detection Initialized"'
    # subprocess.call('espeak '+detection, shell=True)
    
    # Detection loop
    while True:
        time3 = datetime.now() 
        try:    
            for foo in enumerate(camera.capture_continuous(stream,'bgr',use_video_port = True)): #capture from capture_continuous           
                # Tracking fill follow eithe the biggest Hog or Face
                bigHog=[0,0,0,0] 
                bigFace=[0,0,0,0]
                stepperX = 0
                stepperY = 0
                time1 = datetime.now() #<<<check time>>>        
                time2 = time1 #<<<check time>>>
                frame = stream.array #save image array to variable
                stream.seek(0) #initialize stream for next iteration
                stream.truncate()               
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)              
                found,w=hog.detectMultiScale(frame, winStride=(8,8), padding=(32,32), scale=1.05)
                
                #print(found)
                
                # Draw a rectangle around the bodies
                for (x, y, w, h) in found:
					
					# Post to log
					
					
                    print ('body -> x: ',x,', y: ', y ,', A: ', w*h)
                    
                    # Check for bigHog (store only the biggest to track)
                    if w*h > bigHog[2]*bigHog[3] :
                        bigHog=[x, y, w, h]
                        stepperX=x 
                        stepperY=y
                    
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]
                    
                    # ###Speak only once per new detection or every 10 secs
                    # text = '"BODY DETECTED"'
                    # subprocess.call('espeak '+text, shell=True)
                    
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                for (x,y,w,h) in faces:
                    print ('face -> x: ',x,', y: ', y ,', A: ', w*h)
                    # Check for bigHog
                    if w*h > bigFace[2]*bigFace[3] :
                        bigFace=[x, y, w, h]
                        stepperX=x 
                        stepperY=y
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                        # roi_gray = gray[y:y+h, x:x+w]
                        # roi_color = frame[y:y+h, x:x+w]
                        ###EYE DETECTION
                        # eyes = eye_cascade.detectMultiScale(roi_gray)
                        # for (ex,ey,ew,eh) in eyes:
                            # cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                    
                # ### TO DO ... Send something smart to ur Arduino???
                # Send center x,y to Arduino
                # Get largest HOG or FACE (=closest)
                if stepperX != 0 and stepperY != 0:
                    SendMotor(stepperX,stepperY)
                    
                ##TIME STAMP HERE
                timestamp = datetime.now()
                ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
                # print('timestamp')
                cv2.putText(frame, ts, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
                
                # Display frame
                # viddyframe=frame
                cv2.imshow('feed', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        

        finally:
                # When everything is done, release the capture
                # video_capture.release()
                cv2.destroyAllWindows()

############### ROUTER #######################
# Static/public dashboard site
@app.route('/<path:path>')
def index(path):
    # return "hello world"
    return send_from_directory('www/')
    #return render_template('www/index.html')


# Video Route / video injected object 
# create image with src this route and video-feed will be pushed to receiver

# 1. Video stream generator for Video route
def video_gen():
    while True:
        #print(frame)
        ret, jpeg = cv2.imencode('.jpg', frame)
        #return jpeg.tostring()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tostring() + b'\r\n\r\n')

# ### TODO Make it multiple video /video/1/small or large
@app.route('/video')
def video_feed():
    return Response(video_gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Video test-page route HTML page with rendered video feed from camera 1
@app.route('/video/test')
def videotest():
    # return video test-page
    return render_template('videotest.html')

# Voice synthesis / add "text to speak" to payload JSON escaped
@app.route('/api/speak')
def send_speak():
    content = request.json
    #print content['text']
    subprocess.call('espeak '+ content['text'], shell=True)
    #return jsonify({"speak":content['text']})

# TO DO Voice detect


######### MOTOR CONTROL ############

# Pan/tilt Control
#@app.route('/api/control/device/action')
#def send_pantilt(path):
    #return app.send_static_file(path)
    #return redirect(url_for('static', filename='/api/widgets/'+ path))
    #return send_from_directory('api/widgets/', path)

# Control API for GPIO
#@app.route('/api/control/gpio/action')
                
#@app.route('/widget/<path:path>')
#def send_js(path):
#    return send_from_directory('js', path)

    
######### GPIO Routes ############
# GPIO Test page
@app.route("/api/gpio/test")
def gpiotest(): 
    templateData = {
        'pins' : pins
    }
    # render the test-page
    return render_template('gpiotest.html', **templateData)

@app.route("/api/gpio/<changePin>/<action>")
def gpioaction(changePin, action):
    # Convert the pin from the URL into an integer:
    try :
        changePin = int(changePin)
        # Condition inputs
        if action == 1:
            action == "on"  
        
        if action == 0:
            action == "off" 

        # Get the device name for the pin being changed:
        deviceName = pins[changePin]['name']
        # If the action part of the URL is "on," execute the code indented below:
        if action == "on" :
          # Set the pin high:
          GPIO.output(changePin, GPIO.HIGH)
          # Save the status message to be passed into the template:
          message = "Turned " + deviceName + " on."
        if action == "off" :
          GPIO.output(changePin, GPIO.LOW)
          message = "Turned " + deviceName + " off."

       # For each pin, read the pin state and store it in the pins dictionary:
        for pin in pins:
          pins[pin]['state'] = GPIO.input(pin)

        return True
        
    except :
        # Along with the pin dictionary, put the message into the template data dictionary:
        return False

            
    finally :
        # Along with the pin dictionary, put the message into the template data dictionary:
        templateData = {
          'pins' : pins
        }

# API for Widgets
@app.route('/api/widgets/<path:path>')
def send_widget(path):
    print('get widgets called' + path)
    #return app.send_static_file(path)
    #return redirect(url_for('static', filename='/api/widgets/'+ path))
    return send_from_directory('assets/js/widgets/', path)
    #return app.send_static_file('api/widgets/' + path, path)

# API for libraries/js
@app.route('/api/js/<path:path>')
def send_js(path):
    #return app.send_static_file(path)
    #return redirect(url_for('static', filename='/api/js/'+ path))
    return send_from_directory('api/js/', path)

######################## END ROUTER ##################################

def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(log_posts_namespace)
    api.add_namespace(log_categories_namespace)
    flask_app.register_blueprint(blueprint)

    db.init_app(flask_app)


def T4server():
    initialize_app(app)
    log.info('>>>>> Starting T4 server at http://%s:%d/api/ <<<<<', settings.FLASK_SERVER_HOST, settings.FLASK_SERVER_PORT)
    server= app.run(host=settings.FLASK_SERVER_HOST, port=settings.FLASK_SERVER_PORT, threaded=True)  
    #app.run(host=settings.FLASK_SERVER_HOST, port=settings.FLASK_SERVER_PORT, debug=settings.FLASK_DEBUG, threaded=True)

exitapp=False

if __name__ == '__main__':
    #Start server/Router
    t4Server = threading.Thread(name='server', target=T4server)
    t4Server.daemon = True
    # Detection loop
    t4Main = threading.Thread(name='Detect', target=T4main)
    # Action logic
    t4Action = threading.Thread(name='Action', target=T4action)

    try:
        t4Server.start()
        t4Main.start()
        t4Action.start()
    except KeyboardInterrupt:
        exitapp = True
        t4Server.stop()
        t4Main.stop()
        t4Action.stop()
        raise # Let all the threads clean themselves up