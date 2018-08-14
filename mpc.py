#!/usr/bin/env python
# -*- coding: utf8 -*-
# base of Read.py

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import sys
import os
import subprocess
from random import randint

# SoC als Pinreferenz waehlen
GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()
# Pin 24 vom SoC als Input deklarieren und Pull-Down Widerstand aktivieren
GPIO.setup(11, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(15, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(29, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(31, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(32, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(33, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(35, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(36, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(37, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(38, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(40, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

# ISR
def intShutdown(channel):
        os.system('shutdown -h now')
# ISR
def intVolDec(channel):
        os.system('mpc volume -5')
# ISR
def intVolInc(channel):
        os.system('mpc volume +5')
# ISR
def intPlay(channel):
        os.system('mpc play 1')

# ISR
def intStop(channel):
        os.system('mpc stop')

# Interrupt Event hinzufuegen. Pin x, auf steigende Flanke reagieren und ISR "Interrupt" deklarieren
GPIO.add_event_detect(11, GPIO.RISING, callback = intShutdown, bouncetime = 400)
GPIO.add_event_detect(16, GPIO.RISING, callback = intVolDec, bouncetime = 400)
GPIO.add_event_detect(29, GPIO.RISING, callback = intVolInc, bouncetime = 400)
GPIO.add_event_detect(38, GPIO.RISING, callback = intPlay, bouncetime = 400)
GPIO.add_event_detect(40, GPIO.RISING, callback = intStop, bouncetime = 400)



continue_reading = True
v_cont = 1 # read only one UID or =1 continue reading 
v_hex  = 1 # UID as decimal or hexal
v_deb  = 0 # additional information 
cardSN = ""
cardSNold = ""
count_error = 0

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
 global continue_reading
 continue_reading = False
 if v_deb == 1:
  print " Ctrl+C captured, ending read."

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()


mpc = {
"040A3BF1F52580" : "mpc add Bibi40.mp3", 
"36FA6A90" : "mpc add Bibi;", 
"044F3E12062280" : "mpc add Drachen1.mp3;", 
"3B2A41D5":"mpc add Drachen2.mp3;"
}
mpcpre = "mpc volume 65; mpc clear; "
mpcsuf = "mpc play"

while continue_reading:
 (status,TagType,CardTypeRec) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
 if status == MIFAREReader.MI_OK:
  cardTypeNo = CardTypeRec[1]*256+CardTypeRec[0]
  (status,uid,uidData) = MIFAREReader.MFRC522_Anticoll()
  if status == MIFAREReader.MI_OK:
   count_error = 0
   cardType = ""
   
   cardSN = MIFAREReader.list2HexStr(uidData)
   if cardSNold == cardSN:
    # wait one sec. before next read will be started
    time.sleep(5)
   else:
    print cardSN
    ################## Play ##################
    if "mp3" not in mpc[cardSN]: 
        # Handle m3u
        # cat /var/lib/mpd/playlists/Bibi.m3u | wc -l
        lineCount = subprocess.check_output("cat /var/lib/mpd/playlists/"+mpc[cardSN]+".m3u | wc -l", shell=True)
        random = randint(1, lineCount) # get random Interger between 1 and playlist length
        os.system(mpcpre+mpc[cardSN]+mpcsuf+" "+random); # play random position in playlist
    else: 
        # Handle singe mp3
        os.system(mpcpre+mpc[cardSN]+mpcsuf);
    ################## Play ##################
    cardSNold = cardSN
  else:
   cardSNold = ""
 else:
  # Card read error / no Card found
  if count_error>4:
   cardSNold = ""
  count_error = count_error+1
 if v_cont == 0:
  # once must be readed
  if len(cardSN)>1:
   continue_reading = False
GPIO.cleanup()
