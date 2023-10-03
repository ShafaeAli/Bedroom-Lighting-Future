from datetime import datetime
import datetime
from astral.sun import sun
from astral import LocationInfo

from pysolar.solar import*

import RPi.GPIO as GPIO
import pigpio
import time

from flask import Flask
from flask_ask import Ask, statement, convert_errors
import logging

from multiprocessing import Process, Value

import requests

GPIO.setmode(GPIO.BCM)

#LimitSwitchShut = 16
#LimitSwitchOpen = 12
#GPIO.setup(LimitSwitchShut, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(LimitSwitchOpen, GPIO.IN, pull_up_down=GPIO.PUD_UP)

servo = 23
#using pigpio for accurate hardware based timing rather than software generated which is susceptible to jitter

pwm = pigpio.pi() 
pwm.set_mode(servo, pigpio.OUTPUT)
pwm.set_PWM_frequency( servo, 50 )

def get_elevation():
    date = datetime.datetime.now()
    LAT = "REMOVED FOR PRIVACY"
    LON = "REMOVED FOR PRIVACY"
    location = LocationInfo("Home","England","GMT",LAT,LON)
    
    sun_times = sun(location.observer, date = date)

    dawn=sun_times["dawn"]
    dusk=sun_times["dusk"]
    dawn_elevation=get_altitude(LAT,LON,dawn)
    dusk_elevation=get_altitude(LAT,LON,dusk)
    #print(dawn_elevation)

    now = datetime.datetime.now(datetime.timezone.utc)
    #now=datetime.datetime(2007,2,18,12,13,1,190320,tzinfo=datetime.timezone.utc)
    current_elevation = get_altitude(LAT,LON,now)
    return current_elevation, dawn_elevation, dusk_elevation

app = Flask(__name__)
ask = Ask(app, '/')

#logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.intent('CONTROL_Intent', mapping={'status': 'status'})
def gpio_control(status):
    if status == "open":
    
        pwm.set_servo_pulsewidth( servo, 2500 ) ;
        time.sleep(2)
        pwm.set_PWM_dutycycle(servo,0);
        #else:
        #pwm.set_PWM_dutycycle(servo, 0);
    if status == 'close':
        pwm.set_servo_pulsewidth( servo, 500 ) ;
        time.sleep(2)

#else:
        pwm.set_PWM_dutycycle(servo, 0);
    #GPIO.setup(pinNum, GPIO.OUT)
    #if status in ['on', 'high']:    GPIO.output(pinNum, GPIO.HIGH)
    #if status in ['off', 'low']:    GPIO.output(pinNum, GPIO.LOW)
    #return statement('Turning pin {} {}'.format(pin, status))
    #print(status)
    #time.sleep(1)
    return statement('Sensing and IoT is super epic.')
"""
def automate(status):
    while True:
        if status == "close":
            status.value = True
        if status == "open":
            status.value = False
                
        if status.value == True:
            print("true ting")
            #current_elevation, dawn_elevation, dusk_elevation = get_elevation()
            #if current_elevation < dawn_elevation or current_elevation < dusk_aacelevation:
             #   print("it is early morning or night ", current_elevation)
              #  pwm.set_servo_pulsewidth( servo, 500 ) ;
            #elif current_elevation > dawn_elevation or current_elevation > dusk_elevation:
             #   print("it is daytime ", current_elevation)
              #  pwm.set_servo_pulsewidth( servo, 2500 ) ;
        if status.value == False:
            print("false ting")
        time.sleep(1)"""


if __name__=='__main__':
    
    #recording_on=Value('b', True)
    #p = Process (target=automate, args=(recording_on,))
    #p.start()
    app.run(debug=True,use_reloader=False)
    #p.join()

"""

    

#if the current elevation is less than dawn or dusk, then servo should be drivenn till endstop 1 active
#if the current elevation is anything else, then servo should be driven till endstop 2 active
#if the servo has been on for more than x amount of time, shut it down.
try:
    while True:
        current_elevation, dawn_elevation, dusk_elevation = get_elevation()
        #if GPIO.input(LimitSwitchShut):
        if current_elevation < dawn_elevation or current_elevation < dusk_aacelevation:
            print("it is early morning or night ", current_elevation)
            #if GPIO.input(LimitSwitchShut):
            pwm.set_servo_pulsewidth( servo, 500 ) ;
            time.sleep(1)
            #else:
            pwm.set_PWM_dutycycle(servo, 0);
            #pwm.set_PWM_freqduency( servo, 0 );
        elif current_elevation > dawn_elevation or current_elevation > dusk_elevation:
            #print("it is daytime ", current_elevation)
            #if GPIO.input(LimitSwitchOpen):
            pwm.set_servo_pulsewidth( servo, 2500 ) ;
            time.sleep(1)
            #else:
            pwm.set_PWM_dutycycle(servo, 0);
            #pwm.set_PWM_frequency( servo, 0 );
except KeyboardInterrupt:
    print("interrupted")
    pwm.set_PWM_dutycycle(servo, 0)
    pwm.set_PWM_frequency( servo, 0 )
    #pwm.set_PWM_dutycycle(servo, 0)
    #pwm.set_PWM_frequency( servo, 0 )"""



