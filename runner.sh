#!/bin/sh

cd /home/$USER/Desktop/Python_ASSIGNMENT1/Resume_Parser


python -u controller.py | tee -a logfile.txt
