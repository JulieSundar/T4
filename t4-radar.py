################# T4 Detect n Act Security Framework ################
#   Mod: 09/03/2017 16:17
#   Last mod: T4Action functions
#
######################################################################
# import the necessary packages
from __future__ import print_function
from pyimagesearch.basicmotiondetector import BasicMotionDetector
from imutils.video import VideoStream
import numpy as np
import datetime
import imutils
import time
import cv2



#import packages
import sys, os
import serial
import string
import argparse
import time

from datetime import datetime
from datetime import time
from datetime import timedelta
from PIL import Image
from sys import exit
import subprocess
import requests
import json
import RPi.GPIO as GPIO
import string
from flask import Flask, render_template, Response, send_from_directory, url_for
import threading
# API
import logging.config
from flask import Flask, Blueprint



# #Motion imports
# from pyimagesearch.basicmotiondetector import BasicMotionDetector
# from imutils.video import VideoStream
# import imutils

# Add the T4 Folder path to the sys.path list for the dir references to work
sys.path.append(os.path.abspath(".."))

# Local Data API server (FLASK + RestPlus)
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

# API LogServers for Posting Logs (### TODO put in Settings.py)
logCloud = 'http://168.195.218.207:5000/api/log/posts/' # Cloud Logs API for global logs eg Alarms (@Datasur)
logLocal = 'http://localhost:5000/api/log/posts/'       # Local Logs API



# initialize the video streams and allow them to warmup
print("[INFO] starting cameras...")
webcam = VideoStream(src=0).start()
picam = VideoStream(usePiCamera=True).start()

apiframes = [] # Array with all Captured frames side by side
# initialize the two motion detectors, along with the total
# number of frames read
camMotion = BasicMotionDetector()
piMotion = BasicMotionDetector()



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




#################### T4 Main Detection Loop ###################
def T4main():

    #time.sleep(2.0)
    total = 0

    # loop over frames from the video streams
    while True:
    	# initialize the list of frames that have been processed
    	frames = []

        # loop over the frames and their respective motion detectors
        for (stream, motion) in zip((webcam, picam), (camMotion, piMotion)):
            # read the next frame from the video stream and resize
            # it to have a maximum width of 400 pixels
            frame = stream.read()
            #frame = imutils.resize(frame, width=width)

            # convert the frame to grayscale, blur it slightly, update
            # the motion detector
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            locs = motion.update(gray)

            # we should allow the motion detector to "run" for a bit
            # and accumulate a set of frames to form a nice average
            if total < 32:
                frames.append(frame)
                continue

            # otherwise, check to see if motion was detected
            if len(locs) > 0:
                # initialize the minimum and maximum (x, y)-coordinates,
                # respectively
                (minX, minY) = (np.inf, np.inf)
                (maxX, maxY) = (-np.inf, -np.inf)

            # loop over the locations of motion and accumulate the
            # minimum and maximum locations of the bounding boxes
            for l in locs:
                (x, y, w, h) = cv2.boundingRect(l)
                (minX, maxX) = (min(minX, x), max(maxX, x + w))
                (minY, maxY) = (min(minY, y), max(maxY, y + h))

            # draw the bounding box
            cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 3)

            # update the frames list
            frames.append(frame)

        # increment the total number of frames read and grab the 
        # current timestamp
        total += 1
        timestamp = datetime.datetime.now()
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")

        # loop over the frames a second time
        for (frame, name) in zip(frames, ("Webcam", "Picamera")):
            # draw the timestamp on the frame and display it
            cv2.putText(frame, ts, (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            cv2.imshow(name, frame)

        # Add to web stream
        apiframes = frames #zip(frames, ("Webcam", "Picamera"))

        # check to see if a key was pressed
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # do a bit of cleanup
    print("[INFO] cleaning up...")
    cv2.destroyAllWindows()
    webcam.stop()
    picam.stop()






#############################################################


#################### T4 Main Action Loop ###################
# STATUS LOG CATEGORIES
# category_id Category
#   1     Alarm
#   2     Warning
#   3     Message
#   4     System
#   5     Motion Detected
#   6     Body Detected
#   7     Face Detected
def postLog(logServer, json_data):
    headers = {'Content-type': 'application/json'}
    response = requests.post(logServer, data=json_data, headers=headers)
    print(response)

# Detection Params
motionDelay = 5000  # ms threshold/wait before resetting motion detected
bodyDelay   = 5000  #
faceDelay   = 5000

alarmTriggerDelay = 10   # ms before alarm flares
alarmSoundOn      = 10   # min alarm on horn/sound (could be a sequence too start/pause/start x3)
alarmPause        = 1    # mins pause after alarm has been triggered
alarmResetDelay   = 0

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
    ##TIME STAMP HERE
    timestamp2 = datetime.now()
    ts2 = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    data = {"body": "Started T4 server", "category": "System", "title": "T4-Taz_001 started","category_id": 4, "pub_date" : ts2, "end_date" : ts2} #{"data" : "24.3"}
    # Send notification to Local LogServer
    postLog(logLocal, json.dumps(data))


############### ROUTER #######################
# Static dashboard site
@app.route('/<path:path>')
def index(path):
    # return "hello world"
    return send_from_directory('www/')
    #return render_template('www/index.html')


# Video Route / video injected object 
# create image with src this route and video-feed will be pushed to receiver

#  1. Video stream generator for Video route
def video_gen():
    while True:
        print(apiframes)
        ret, jpeg = cv2.imencode('.jpg', apiframes)
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
    log.info('>>>>> Starting T4 Radar at http://%s:%d/api/ <<<<<', settings.FLASK_SERVER_HOST, settings.FLASK_SERVER_PORT)
    server= app.run(host=settings.FLASK_SERVER_HOST, port=settings.FLASK_SERVER_PORT, threaded=True)  
    #app.run(host=settings.FLASK_SERVER_HOST, port=settings.FLASK_SERVER_PORT, debug=settings.FLASK_DEBUG, threaded=True)

runApp=True

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
        #t4Action.start()
    except KeyboardInterrupt:
        runApp = False
        t4Server.stop()
        t4Main.stop()
        #t4Action.stop()
        raise # Let all the threads clean themselves up
