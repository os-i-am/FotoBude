from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import board
import neopixel
import signal, glob, os, subprocess, sys
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

#display idle screen
def idleScreen():
    #while True:
        os.system("sudo killall FBpyGIF")
        os.system("sudo killall fbi")
        subprocess.Popen(['FBpyGIF', '/mnt/FotoBude/waitingOwl.gif'])
        #wait(60)
        #os.system("sudo fbi -a --noverbose -T 2 /mnt/FotoBude/sleeping.jpg")
        #sleep(10)
        #os.system("sudo fbi -a --noverbose -T 2 /mnt/FotoBude/preCapture-arrow.jpg")
        #sleep(10)


# pre-capture lightshow
def preCaptureLights () :
    os.system("sudo killall FBpyGIF")
    #------------------------
    GPIO.output(16, GPIO.LOW)
    os.system("sudo fbi -a --noverbose -T 2 /mnt/FotoBude/preCapture-5.jpg")
    sleep(0.5)
    GPIO.output(16, GPIO.HIGH)
    #------------------------
    GPIO.output(20, GPIO.LOW)
    sleep(0.5)
    GPIO.output(20, GPIO.HIGH)
    #------------------------
    GPIO.output(21, GPIO.LOW)
    os.system("sudo fbi -a --noverbose -T 2 /mnt/FotoBude/preCapture-4.jpg")
    sleep(0.5)
    GPIO.output(21, GPIO.HIGH)
    #------------------------
    GPIO.output(16, GPIO.LOW)
    sleep(0.5)
    GPIO.output(16, GPIO.HIGH)
    #------------------------
    GPIO.output(20, GPIO.LOW)
    os.system("sudo fbi -a --noverbose -T 2 /mnt/FotoBude/preCapture-3.jpg")
    sleep(0.5)
    GPIO.output(20, GPIO.HIGH)
    #------------------------
    GPIO.output(21, GPIO.LOW)
    sleep(0.5)
    GPIO.output(21, GPIO.HIGH)
    os.system("sudo fbi -a --noverbose -T 2 /mnt/FotoBude/preCapture-arrow.jpg")
    led_ring_show(0.001)
    #sleep(1.5)
    os.system("sudo fbi -a --noverbose -T 2 /mnt/FotoBude/preCapture-black.jpg")

#NeoPixel Ring
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

# NeoPixel Ring
def led_ring_show(wait):
    for x in range(2):
        for j in range(255):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255)
            pixels.show()
            sleep(wait)
    #pixels.fill((255, 255, 255))
    #pixels.show()

#NeoPixel Ring off
def led_ring_off():
    pixels.fill((0, 0, 0))
    pixels.show()

# capture image
def captureImage () :
    os.system("sudo fbi -a --noverbose -T 2 /mnt/FotoBude/loading.jpg") 
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

    #os.system("sudo killall FBpyGIF")
    os.system("sudo fbi -a --noverbose -T 2 " + recent_img[0])
    sleep (5)

# ArcadeButton press routine
def button_pressed(channel):
    sleep(0.1)
    if (GPIO.input(channel) == False):
        GPIO.output(LED_PIN, False)
        preCaptureLights()
        captureImage()
        led_ring_off()
        print("image captured")
        displayMostRecentImage()
        GPIO.output(LED_PIN, True)
        idleScreen()

# LockTrigger routine
def lock_trigger(channel):
    print("Button was pushed!")
    if (GPIO.input(channel) == True):
        subprocess.call(['killall', 'mpg123'])
        sleep(0.1)
        subprocess.Popen(['mpg123', '/mnt/FotoBude/americano.mp3'])

# kill Music (if playing)
def kill_music(channel):
    if (GPIO.input(channel) == True):
        subprocess.call(['killall', 'mpg123'])

# shutdown gracefully
def shutdown(signal, frame):
  print("..shutting down")
  subprocess.call(['FBpyGIF', '-c'])
  subprocess.call(['killall', 'FBpyGIF'])
  subprocess.call(['killall', 'mpg123'])
  subprocess.call(['killall', 'fbi'])
  #os.system('clear')  
  GPIO.output(LED_PIN, False)
  GPIO.cleanup()
  sys.exit(0)


##################
# PRE-LOOP SETUP #
##################

GPIO.setmode(GPIO.BCM)

# Relay Setup (GPIO)
# 1  -->   GPIO 12
# 2  -->   GPIO 16
# 3  -->   GPIO 20
# 4  -->   GPIO 21

gpioList = [12, 16, 20, 21]
for i in gpioList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

# GPIO setup
BTN_PIN = 19
LED_PIN = 26

# NeoPixel 32-LED Ring setup
NEO_PIN = board.D18 # --> GPIO 18
num_pixels = 32
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    NEO_PIN, num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER
)

LockTrigger_PIN = 6
killMusic_PIN = 5

GPIO.setwarnings(False)
GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #LockTrigger
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #killMusic

# general setup

killgp2()
createSaveFolder()
os.system("sudo killall cron")
os.system("sudo killall -TERM dietpi-update")
print("...ready")
GPIO.output(LED_PIN, True)


#############
# MAIN LOOP #
#############

# eventListener for Buttons
GPIO.add_event_detect(BTN_PIN, edge = GPIO.RISING, callback = button_pressed, bouncetime = 300)
GPIO.add_event_detect(LockTrigger_PIN, edge = GPIO.RISING, callback = lock_trigger, bouncetime = 300)
GPIO.add_event_detect(killMusic_PIN, edge = GPIO.RISING, callback = kill_music, bouncetime = 300)

#shutdown trigger
signal.signal(signal.SIGINT, shutdown)

idleScreen()

while True:
  sleep(1)