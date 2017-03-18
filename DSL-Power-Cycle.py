#!/usr/bin/python

import os
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(4,GPIO.OUT)
GPIO.output(4,GPIO.HIGH) # Relay control pin

#Dictionary for which pin each LED color is on
led_gpio = {}
led_gpio['green'] = 16
led_gpio['yellow'] = 20
led_gpio['red'] = 21

#Setup the pins used in the dictionary above
GPIO.setup(16,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)

hosttoping = "8.8.8.8"
sucdelay = 120 # How many seconds to wait after a successful ping
failretry = 3 # How many cycles of failed pings before power cycle
faildelay = 30 # How long to wait after a failed ping before trying again
poweroffdelay = 10 # How long to stay powered off
bootdelay = 180 # How many seconds to wait after power cycle 
circlekdelay = 600 # How long to wait after a power cycle failed before starting over
circlek = False
VERBOSE = True

def led(color):
   if color == 'off':
      for led_off in led_gpio: #Switch all LED's off
         GPIO.output(led_gpio[led_off],GPIO.LOW)
   else:
      for led_off in led_gpio: #Switch all LED's off
         GPIO.output(led_gpio[led_off],GPIO.LOW)
      GPIO.output(led_gpio[color],GPIO.HIGH)

def ping(host):
   print "Pinging " + hosttoping + " on eth0"
   response = os.system("ping -c 1 -I eth0 -W 2 " + host + "  >/dev/null 2>&1" )
   if response == 0:
      return True
   else:
      return False

def logme(logmsg):
   os.system("logger -i -t DSL -p local7.info \"" + logmsg + "\"" )

def vprint(*args):
    # Verbose printing happens here
    # Called from other locations like this
    #  vprint ("Look how awesome my verbosity is")
    # This function is enabled by the -v switch on the CLI
    if VERBOSE:
        for arg in args:
           print arg
           logme(arg)

def kickit():
   global circlek
   led('red')
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
      led('green')
      print "OK it's working again, returning to our normaly scheduled programming."
      time.sleep(sucdelay)
   else:
      circlek = True

def cleanup():
   GPIO.output(4,GPIO.HIGH)
   GPIO.cleanup()

logme ("Test log entry from inside the system while pinging " + hosttoping + " this host.") 
led('off')
while True:
   if circlek == True:
      print "Strange things are afoot at the Circle-K, so we're going to sleep for " + str(circlekdelay) + " and then try again."
      time.sleep(circlekdelay)
      print "OK lets try this again."
      circlek = False
   if ping(hosttoping):
      led('green')
      print "Yep it's pingable. So we're going to sleep for " + str(sucdelay) + " seconds before checking again."
      time.sleep(sucdelay);
      led('off')
   else:
      led('yellow')
      print "Nope it didn't answer. Crap!" 
      retrycount = 0
      while retrycount <= failretry:
         print "Sleeping for " + str(faildelay) + " seconds before we try pinging again."
         time.sleep(faildelay)
         led('off')
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
               led('yellow')
               print "It still wasn't pingable after " + str(retrycount) + " tries." 
               print "We will keep trying until we have tried " + str(failretry) + " times."

