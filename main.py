import os
import picamera
import time
import RPi.GPIO as GPIO
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEBase import MIMEBase
from email import Encoders
import subprocess
import smtplib
import socket
import config
import pygame
import io


total_pics = 4 # number of pics  to be taken
capture_delay = 3 # delay between pics
file_path = '/home/pi/photobooth/pics/'
file_path_arch = '/home/pi/PB_archive/'
now = time.strftime("%H%M%S")
led1_pin = 18
button1_pin = 17
test_server = 'google.com'
addr_to   = '*****************' 
addr_from = '******************' # change to your full gmail address
user_name = '************' # change to your gmail username
password = '*********' # change to your gmail password
test_server = 'www.google.com'
WIDTH=1280
HEIGHT=1024
FONTSIZE=50
## b/w
##camera.saturation = -100
camera = picamera.PiCamera()
##camera.resolution = (500, 375) #use a smaller size to process faster, and tumblr will only take up to 500 pixels wide for animated gifs
camera.resolution = (1024, 768)
camera.vflip = True
camera.hflip = True



GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(led1_pin,GPIO.OUT) # LED 1
GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # LED 2
GPIO.output(led1_pin,False);

def preview(timeDelay, status='r'):
    
    pygame.init()
    timeout = 1
    ticker = 0
    PRsize = (1024,768)
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    font = pygame.font.SysFont('freeserif', 42, bold=1)
    clk = pygame.time.Clock()
    clk.tick()
    if (status == 'r'):
        rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
        while (timeDelay):
            clk.tick()
            stream = io.BytesIO()
            camera.capture(stream, use_video_port=True, format='rgb', resize=PRsize)
            stream.seek(0)
            stream.readinto(rgb)
            stream.close()
     
            img = pygame.image.frombuffer(rgb[0:(PRsize[0] * PRsize[1] * 3)], (PRsize[0], PRsize[1]), 'RGB')
            screen.blit(img, (0,0))
     
            
            
            ticker+=clk.get_time()
            if (ticker > 2000):
                ticker = 0
                timeDelay=timeDelay - 1
            text = ":)  Smile   NOW   !!  " + str(timeDelay) 
            textSurface = font.render(text, 1, pygame.Color(255, 255, 255))
            screen.blit(textSurface, (280, 380))
     
            # finally update and display the image
            pygame.display.update()
            
        screen.fill((255, 255, 255))
        pygame.display.update()
    elif (status == 'p'):
        text = "Please Wait "
        screen.fill((255, 255, 255))
        textSurface = font.render(text, 1, pygame.Color(255, 0, 0))
        screen.blit(textSurface, (280, 380))
        pygame.display.update()
    elif (status == 'w'):
        text = "Ready !! Press the BIG red button"
        screen.fill((255, 255, 255))
        textSurface = font.render(text, 1, pygame.Color(255, 0, 0))
        screen.blit(textSurface, (280, 380))
        pygame.display.update()
        

def start_photobooth():
    while (True):
        

        

#         camera.start_preview()
        preview(3)
        try: #take the photos
            for i, filename in enumerate(camera.capture_continuous(file_path + now + '-' + '{counter:02d}.jpg')):
                print(filename)
               ## time.sleep(0.25) #pause the LED on for just a bit
               ## time.sleep(capture_delay) # pause in-between shots
                preview(4)
                if i == total_pics-1:
                    GPIO.output(led1_pin,False);
                    break
        finally:
            camera.close()
            break

def is_connected():
    try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
        host = socket.gethostbyname(test_server)
    # connect to the host -- tells us if the host is actually
    # reachable
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

def send_email():
    try:
        msg = MIMEMultipart()
        msg['Subject'] = "Photo Booth " + now
        msg['From'] = addr_from
        msg['To'] = addr_to
        file_to_upload = file_path_arch +"PB_"+now + ".jpg"
        print file_to_upload
        fp = open(file_to_upload, 'rb')
        part = MIMEBase('image', 'jpg')
        part.set_payload( fp.read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_to_upload))
        fp.close()
        msg.attach(part)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(user_name, password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print "email sent"
    except ValueError:
        print "Oops. No internect connection. Upload later."
        try: #make a text file as a note to upload the .gif later
            file = open(file_path + now + "-FILENOTUPLOADED.txt",'w')   # Trying to create a new file or open one
            file.close()
        except:
            print('Something went wrong. Could not write file.')
            sys.exit(0) # quit Python


def printPic():
    cmd = ['sudo', './print.sh', now]
    pr = subprocess.Popen(cmd)
    pr.wait()

while True:
    preview(1,'w')
    GPIO.output(led1_pin,True);
    ##print "Get Ready" 
    GPIO.wait_for_edge(button1_pin, GPIO.FALLING)
    GPIO.output(led1_pin,False);
    time.sleep(0.2) #debounce
    start_photobooth()
    preview(1,'p')
    printPic()
    if (is_connected()):
        send_email()
    GPIO.output(led1_pin,True);
    

