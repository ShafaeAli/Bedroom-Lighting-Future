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
    LAT = 'REMOVED'
    LON = 'REMOVED'
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
    
try:
    while True:
        current_elevation, dawn_elevation, dusk_elevation = get_elevation()
        if current_elevation < dawn_elevation or current_elevation < dusk_elevation:
            print("it is early morning or night ", current_elevation)
            pwm.set_servo_pulsewidth( servo, 500 ) ;
            time.sleep(1)
            pwm.set_PWM_dutycycle(servo, 0);
        elif current_elevation > dawn_elevation or current_elevation > dusk_elevation:
            #print("it is daytime ", current_elevation)
            pwm.set_servo_pulsewidth( servo, 2500 ) ;
            time.sleep(1)
            pwm.set_PWM_dutycycle(servo, 0);
            
except KeyboardInterrupt:
    print("interrupted")
    pwm.set_PWM_dutycycle(servo, 0)
    pwm.set_PWM_frequency( servo, 0 )



