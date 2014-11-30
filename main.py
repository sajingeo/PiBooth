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
from config import *


## b/w
##camera.saturation = -100
camera = picamera.PiCamera()
camera.resolution = (800, 480)
camera.vflip = True
camera.hflip = True



GPIO.cleanup()
GPIO.setmode(GPIO.BCM)    
GPIO.setup(led1_pin,GPIO.OUT) # LED 1
GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Big RED button
GPIO.output(led1_pin,False);

def preview(timeDelay, status='r'):
    pygame.init()
    timeout = 1
    ticker = 0
    PRsize = (800,480)
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    font = pygame.font.SysFont('freeserif', 38, bold=1)
    font1 = pygame.font.SysFont('freeserif', 42, bold=1)
    clk = pygame.time.Clock()
    clk.tick()
    if (status == 'r'):
        rgb = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
        ## Preview Loop
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
            text = ":)  SMILE   NOW   !!  " + str(timeDelay) 
            textSurface = font.render(text, 1, pygame.Color(255, 255, 255))
            textSurface = pygame.transform.rotate(textSurface,90)
            screen.blit(textSurface, (400, 80))
     
            # finally update and display the image
            pygame.display.update()
            
        screen.fill((255, 255, 255))
        pygame.display.update()
    
    ## Processing Screen
    elif (status == 'p'):
        text = "  Wait.... "
        screen.fill((255, 255, 255))
        textSurface = font.render(text, 1, pygame.Color(255, 0, 0))
        textSurface = pygame.transform.rotate(textSurface,90)
        screen.blit(textSurface, (400, 175))
        pygame.display.update()
    
    ## Waiting Screen
    elif (status == 'w'):
        text1 = "READY ?"
        text = "HIT THE"
        text2 ="BIG RED BUTTON"
        screen.fill((255, 255, 255))
        font = pygame.font.SysFont('freeserif', 34, bold=1)
        textSurface1 = font1.render(text1, 1, pygame.Color(0,255,0))
        textSurface1 = pygame.transform.rotate(textSurface1,90)
        textSurface = font.render(text, 1, pygame.Color(255, 0, 0))
        textSurface = pygame.transform.rotate(textSurface,90)
        textSurface2 = font.render(text2, 1, pygame.Color(255, 0, 0))
        textSurface2 = pygame.transform.rotate(textSurface2,90)
        screen.blit(textSurface1, (300, 145))
        screen.blit(textSurface, (450, 175))
        screen.blit(textSurface2, (500, 91))
        pygame.display.update()
        

def start_photobooth():
    ##for the first PIC
    preview(3)
    
    while (True):
        try: #take the photos
            for i, filename in enumerate(camera.capture_continuous(file_path + now + '-' + '{counter:02d}.jpg')):
                print(filename)
               ## time.sleep(0.25) #pause the LED on for just a bit
               ## time.sleep(capture_delay) # pause in-between shots
                if i == total_pics-1:
                    GPIO.output(led1_pin,False);
                    break
                preview(3)
        finally:
            camera.close()
            break

## check internet connection
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

## Send Email with pic
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

## send print script and create image
def printPic():
    cmd = ['sudo', './print.sh', now]
    pr = subprocess.Popen(cmd)
    pr.wait()


## Main Loop
while True:
    preview(1,'w')
    GPIO.output(led1_pin,True);
    ##wait for button press 
    GPIO.wait_for_edge(button1_pin, GPIO.FALLING)
    GPIO.output(led1_pin,False);
    time.sleep(0.2) #debounce button press
    start_photobooth()
    preview(1,'p')
    printPic()
    if (is_connected()):
        send_email()
    GPIO.output(led1_pin,True);
    