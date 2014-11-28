#!/bin/bash
mogrify -resize 968x648 /home/pi/photobooth/pics/*.jpg
montage /home/pi/photobooth/pics/*.jpg -tile 2x2 -geometry +10+10 /home/pi/temp_montage2.jpg
montage /home/pi/temp_montage2.jpg /home/pi/photobooth/photobooth_label.jpg -tile 2x1 -geometry +5+5 /home/pi/temp_montage3.jpg
suffix=$1
cp /home/pi/temp_montage3.jpg /home/pi/PB_archive/PB_${suffix}.jpg
rm /home/pi/photobooth/pics/*.jpg
rm /home/pi/temp*
