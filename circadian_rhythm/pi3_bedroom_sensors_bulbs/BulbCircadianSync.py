from time import sleep, strftime, time

import numpy as np
import colour

from astral.sun import sun
from astral import LocationInfo

from pysolar.solar import*

import tinytuya

from datetime import datetime
import datetime

TEMP_DAY = 255 #255 equivalent to 6000K
TEMP_NIGHT = 0 #0 equivalent to 2700K

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


################################################################################################################################
#SMART BULB

#smart_plug = tinytuya.OutletDevice('REMOVED FOR PRIVACY', 'REMOVED FOR PRIVACY', 'REMOVED FOR PRIVACY')
#smart_plug.set_version(3.3)

bulb1 = tinytuya.BulbDevice('REMOVED FOR PRIVACY', 'REMOVED FOR PRIVACY', 'REMOVED FOR PRIVACY')
bulb1.set_version(3.1)

bulb2 = tinytuya.BulbDevice('REMOVED FOR PRIVACY', 'REMOVED FOR PRIVACY', 'REMOVED FOR PRIVACY')
bulb2.set_version(3.1)

bulb3 = tinytuya.BulbDevice('REMOVED FOR PRIVACY', 'REMOVED FOR PRIVACY', 'REMOVED FOR PRIVACY')
bulb3.set_version(3.1)

bulb4 = tinytuya.BulbDevice('REMOVED FOR PRIVACY', 'REMOVED FOR PRIVACY', 'REMOVED FOR PRIVACY')
bulb4.set_version(3.1)

##########################################################################
def bulb_room_set(bulb1, bulb2, bulb3, bulb4, dip_state, variable):
    bulb1.set_value(dip_state,variable)
    bulb2.set_value(dip_state,variable)
    bulb3.set_value(dip_state,variable)
    bulb4.set_value(dip_state,variable)

def bulb_status(bulb1, bulb2, bulb3, bulb4):
    bulb1data=bulb1.status()
    bulb2data=bulb2.status()
    bulb3data=bulb3.status()
    bulb4data=bulb4.status()
    
    bulb1_state=bulb1data['dps']['1']
    bulb2_state=bulb2data['dps']['1']
    bulb3_state=bulb3data['dps']['1']
    bulb4_state=bulb4data['dps']['1']
    
    return bulb1_state, bulb2_state, bulb3_state, bulb4_state

def elevation_to_col_temp(elevation, TEMP_DAY, TEMP_NIGHT, ELEV_MAX, ELEV_MIN):
    col_temp = TEMP_NIGHT + (TEMP_DAY - TEMP_NIGHT)*((elevation- ELEV_MAX)/(ELEV_MIN - ELEV_MAX))
    return col_temp

#########################################################################

#switch_state = True
#bulb_state = True
#bulb_brightness = 255
#bulb_colour_temp = 0

#########################################################################

now = datetime.datetime.now(datetime.timezone.utc)
#now=datetime.datetime(2007,2,18,18,13,1,190320,tzinfo=datetime.timezone.utc)
current_elevation, ELEV_MIN, ELEV_MAX = get_elevation()
temperature = elevation_to_col_temp(current_elevation, TEMP_DAY, TEMP_NIGHT, ELEV_MAX, ELEV_MIN)
temperature = int(temperature)
print(now)
print("Outside Colour Temp (in terms of bulb value 0-255): ",temperature)
print(current_elevation)

b1,b2,b3,b4 = bulb_status(bulb1, bulb2, bulb3, bulb4)

if b1 and b2 and b3 and b4:
    #bulb_room_set(bulb1, bulb2, bulb3, bulb4, '1', bulb_state)
    #bulb_room_set(bulb1, bulb2, bulb3, bulb4, '2', bulb_brightness)
    bulb_room_set(bulb1, bulb2, bulb3, bulb4, '3', temperature)
    print("Room colour set")
    print (bulb1.status())
    print("\n")
else:
    print("User has set room to off")
    print("\n")