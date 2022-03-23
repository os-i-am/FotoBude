from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, glob, os, subprocess
import RPi.GPIO as GPIO

#############
# VARIABLES #
#############

# file naming variables
shot_date = datetime.now().strftime("%d.%m.%Y")
shot_time = datetime.now().strftime("%H:%M:%S")
picID = "_FotoBude"

# clear command: delete ALL images on camera CF
# deleteCF = ["--folder", "/store_00010001/DCIM/100EOS5D", \
#              "-R", "--delete-all-files"]

# trigger command for the camera
triggerCam = ["--capture-image-and-download"]
keepOnCF = ["--keep"]

# setup folder structure and save location
folder_name = shot_date + picID
save_location = "/mnt/FotoBude/images/" + folder_name

#############
# FUNCTIONS #
#############

# kill gphoto2 process at startup
def killgp2 () :
    p = subprocess.Popen (['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate ()

    # Search for the gphoto process ID (pid)
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
        if len(filename) < 13:
            os.rename (filename, (shot_time +  ID + ".JPG"))
            print ("Renamed the JPG")

def displayMostRecentImage () :    
    files_path = os.path.join(save_location, '*')
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)

    recent_img = [
        files[0],
#       files[1],
#       files[2],
#       files[3]
    ]

    os.system("sudo fbi -a --noverbose -T 2 " + recent_img[0])
    sleep (5)
    #os.system("sudo killall fbi")
    os.system("sudo fbi -a --noverbose -T 2 /mnt/FotoBude/ready.jpg")

#################
# PROGRAM START #
#################

killgp2()
# gp(deleteCF)
createSaveFolder()

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
print("...ready")

# main loop
os.system("sudo fbi -a --noverbose -T 2 /mnt/FotoBude/ready.jpg")

while True :
    if GPIO.input(15) == GPIO.HIGH:
        captureImage()

        #renameFiles(picID)
        print("image captured")

        displayMostRecentImage()
        
 

                       
                       
