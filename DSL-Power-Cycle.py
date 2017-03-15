#!/usr/bin/python

import os
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)
GPIO.output(4,GPIO.HIGH)

hosttoping = "8.8.8.8"
sucdelay = 120 # How many seconds to wait after a successful ping
failretry = 3 # How many cycles of failed pings before power cycle
faildelay = 30 # How long to wait after a failed ping before trying again
poweroffdelay = 10 # How long to stay powered off
bootdelay = 180 # How many seconds to wait after power cycle 
circlekdelay = 600 # How long to wait after a power cycle failed before starting over
circlek = False

def ping(host):
   print "Pinging " + hosttoping + " on eth0"
   response = os.system("ping -c 1 -I eth0 -W 2 " + host + "  >/dev/null 2>&1" )
   if response == 0:
      return True
   else:
      return False

def kickit():
   global circlek
   print "Switching power off."
   GPIO.output(4,GPIO.LOW)
   print "Power is off sleeping for " + str(poweroffdelay) + " seconds before switching it back on."
   time.sleep(poweroffdelay)
   GPIO.output(4,GPIO.HIGH)
   print "Power is on."
   print "Sleeping for " + str(bootdelay) + " seconds for things to reboot."
   time.sleep(bootdelay)
   print "Pinging after reboot."
   if ping(hosttoping):
      print "OK it's working again, returning to our normaly scheduled programming."
      time.sleep(sucdelay)
   else:
      circlek = True

def cleanup():
   GPIO.output(4,GPIO.HIGH)
   GPIO.cleanup()

while True:
   if circlek == True:
      print "Strange things are afoot at the Circle-K, so we're going to sleep for " + str(circlekdelay) + " and then try again."
      time.sleep(circlekdelay)
      print "OK lets try this again."
      circlek = False
   if ping(hosttoping):
      print "Yep it's pingable. So we're going to sleep for " + str(sucdelay) + " seconds before checking again."
      time.sleep(sucdelay);
   else:
      print "Nope it didn't answer. Crap!" 
      retrycount = 0
      while retrycount <= failretry:
         print "Sleeping for " + str(faildelay) + " seconds before we try pinging again."
         time.sleep(faildelay)
         if ping(hosttoping):
            print "It's pingable now"
            break
         else:
            if retrycount >= failretry:
               print "It hasn't been pingable for too long so we're going to kick it." 
               kickit()
               break
            else:
               retrycount += 1
               print "It still wasn't pingable after " + str(retrycount) + " tries." 
               print "We will keep trying until we have tried " + str(failretry) + " times."

