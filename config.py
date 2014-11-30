import time
## you have to reduce you Gmail security from GMAIL account setting and also disable captha
total_pics = 4 # number of pics  to be taken
capture_delay = 3 # delay between pics
file_path = '/home/pi/photobooth/pics/'  ## path to temp pics
file_path_arch = '/home/pi/PB_archive/'  ## path for back up
now = time.strftime("%H%M%S")  ## get time for storing the pic
led1_pin = 18    ## LED Pin
button1_pin = 17   ## Button Bin
test_server = 'google.com'
##addr_to   = 'few61order@photos.flickr.com' # The special tumblr auto post email address
addr_to   = '*****'  ## send address 
addr_from = '*****' # change to your full gmail address
user_name = '*****' # change to your gmail username
password = '*****' # change to your gmail password
test_server = 'www.google.com'
WIDTH=800
HEIGHT=480

