from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess
import RPi.GPIO as GPIO

#############
# VARIABLES #
#############

# file naming variables
shot_date = datetime.now().strftime("%d.%m.%Y")
shot_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
picID = "_FotoBude"

# clear command: delete ALL images on camera CF
# deleteCF = ["--folder", "/store_00010001/DCIM/100EOS5D", \
#              "-R", "--delete-all-files"]

# trigger command for the camera
triggerCam = ["--capture-image-and-download"]
keepOnCF = ["--keep"]

# setup folder structure and save location
folder_name = shot_date + picID
save_location = "/home/pi/Desktop/gphoto/images/" + folder_name

#############
# FUNCTIONS #
#############

# kill gphoto2 process that starts
# whenever the camera gets connected
def killgp2 () :
    p = subprocess.Popen (['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate ()

    # Search for the Process ID (pid)
    # that has thegphoto2 process 
    for line in out.splitlines () :
        if b'gvfsd-gphoto2' in line:
            # Kill found process
            pid = int (line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)

# try to create save folder (if not
# exist already) and change to it
def createSaveFolder () :
    try:
        os.makedirs(save_location)
        print ("Today's directory created")
    except:
        print ("Today's directory already exists... skipping")
    os.chdir(save_location)

# capture image
def captureImage () :
    gp(triggerCam, keepOnCF)

# rename images
def renameFiles (ID) :
    for filename in os.listdir(".") :
        if len(filename) < 13 :
            os.rename (filename, (shot_time + ID + ".JPG"))
            print ("Renamed the JPG")

#################
# PROGRAM START #
#################

killgp2()
# gp(deleteCF)
createSaveFolder()

# GPIO setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
print("...ready")

# main loop
while True :
    if GPIO.input(10) == GPIO.HIGH:
        captureImage()
        print("image captured")