import urllib.request
import requests
import threading
from time import sleep, strftime, time

from bh1745 import BH1745
import numpy as np
import colour

import datetime
from pysolar.solar import*

from astral.sun import sun
from astral import LocationInfo

import time
import board
import adafruit_dht

import smbus

bh1745 = BH1745()
bh1745.setup()
bh1745.set_leds(0)

LAT = "REMOVED FOR PRIVACY"
LON = "REMOVED FOR PRIVACY"
TEMP_DAY = 6000
TEMP_NIGHT = 0

dhtDevice = adafruit_dht.DHT22(board.D17, use_pulseio=False)

previous_room_temp = 0
previous_humidity = 0
##########################################

def get_elevation():
    date = datetime.datetime.now()
    LAT = "REMOVED FOR PRIVACY"
    LON = "REMOVED FOR PRIVACY"
    location = LocationInfo("Home","England","GMT",LAT,LON)
    
    sun_times = sun(location.observer, date = date)

    dawn=sun_times["dawn"]
    dusk=sun_times["dusk"]
    noon=sun_times["noon"]
    dawn_elevation=get_altitude(LAT,LON,dawn)
    dusk_elevation=get_altitude(LAT,LON,dusk)
    noon_elevation=get_altitude(LAT,LON,noon)
    #print(dawn_elevation)

    now = datetime.datetime.now(datetime.timezone.utc)
    #now=datetime.datetime(2007,2,18,12,13,1,190320,tzinfo=datetime.timezone.utc)
    current_elevation = get_altitude(LAT,LON,now)
    return current_elevation, dusk_elevation, noon_elevation

##########################################

def elevation_to_col_temp(elevation, TEMP_DAY, TEMP_NIGHT, ELEV_MAX, ELEV_MIN):
    col_temp = TEMP_NIGHT + (TEMP_DAY - TEMP_NIGHT)*((elevation- ELEV_MAX)/(ELEV_MIN - ELEV_MAX))
    return col_temp

###########################################

def rgb_light():
    bh1745.set_measurement_time_ms(160)
    r, g, b = bh1745.get_rgb_scaled()
    #time.sleep(2)
    return(r,g,b)

def RGB_to_CCT(r,g,b):
    if r > 0 or g > 0 or b > 0:
        RGB=np.array([r,g,b])
        XYZ=colour.sRGB_to_XYZ(RGB/255)
        xy=colour.XYZ_to_xy(XYZ)
        CCT=colour.xy_to_CCT(xy, 'hernandez1999')
        if CCT < 0:
            return 0
        else:
            return CCT
    else:
        return 0
    
    
def lux_measure():
    bus = smbus.SMBus(1)
    bus.write_byte_data(0x38, 0x41, 0x00)
    bus.write_byte_data(0x38, 0x42, 0x90)
    bus.write_byte_data(0x38, 0x44, 0x02)
    time.sleep(0.5)
    data = bus.read_i2c_block_data(0x38, 0x50, 8)
    cData = data[7] * 256 + data[6]
    return cData
        

##############################################
def get_temp():
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        return temperature_c,humidity
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        return 0,0
    except Exception as error:
        dhtDevice.exit()
        return 0,0
##############################################
def sensor_record(previous_room_temp,previous_humidity):
    
    r,g,b=rgb_light()
    CCT=RGB_to_CCT(r,g,b)
    print('RGB: {:10.1f} {:10.1f} {:10.1f}'.format(r, g, b))
    print("Indoor Colour Temp: ", CCT)
    
    white_lux=lux_measure()
    print ("{} lux".format(white_lux))
    
    #now = datetime.datetime.now(datetime.timezone.utc)
    #now=datetime.datetime(2007,2,18,18,13,1,190320,tzinfo=datetime.timezone.utc)
    elevation, ELEV_MIN, ELEV_MAX = get_elevation()
    temperature=elevation_to_col_temp(elevation, TEMP_DAY, TEMP_NIGHT, ELEV_MAX, ELEV_MIN)
    print("Outside Colour Temp: ",temperature)
    
    room_temp_deg,humidity=get_temp()
    print("Temp: {:.1f} C Humidity: {}% \n".format(room_temp_deg, humidity))
    
    if room_temp_deg == 0:
        room_temp_deg = previous_room_temp
        #print ("error corrected")
    if humidity == 0:
        humidity = previous_humidity
        #print ("error corrected")
    #print(room_temp_deg, humidity)
    return CCT,temperature,white_lux,room_temp_deg,humidity

###############################################################################################

def send_to_thingspeak(CCT,temperature,white_lux,room_temp_deg,humidity):
    #threading.Timer(30,thingspeak).start()
    #print("Starting ThingSpeak Connection")
    HEADER='&field1={}&field2={}&field3={}&field4={}&field5={}'.format(CCT,temperature,white_lux,room_temp_deg,humidity)
    URL='https://api.thingspeak.com/update?api_key=XXXXXXX'+HEADER
    data=urllib.request.urlopen(URL)
    #print(data)

##############################################    
while True:
    try:
        CCT,temperature,white_lux,room_temp_deg,humidity = sensor_record(previous_room_temp,previous_humidity)
        previous_room_temp = room_temp_deg
        previous_humidity = humidity
        send_to_thingspeak(CCT,temperature,white_lux,room_temp_deg,humidity)
        with open ("/home/pi/Desktop/ThingSpeakLight/SIoT_Bedroom_Light.csv","a") as log:
            log.write("{0},{1},{2},{3},{4},{5}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(CCT),str(temperature),str(white_lux),str(room_temp_deg),str(humidity)))
        sleep(60)
    except Exception as e:
        print (e)