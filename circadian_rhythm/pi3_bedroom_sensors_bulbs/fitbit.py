import requests
import urllib.request
from datetime import datetime
import datetime
import pandas as pd

import http.client
import urllib
import time
import csv

###############################################################

today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
sleep_url=("https://api.fitbit.com/1.2/user/-/sleep/date/"+ today +".json")
#print(today)

access_token = "REMOVED FOR PRIVACY"
header = {'Authorization': 'Bearer {}'.format(access_token)}
response = requests.get(sleep_url, headers=header).json()

sleep_dict=response['sleep']
sleep_start=sleep_dict[0]['startTime']

sleep_end=sleep_dict[0]['endTime']
size_sleep_end=len(sleep_end)
sleep_end_short = (sleep_end)[:size_sleep_end - 4]

#sleep_end_short_UTC = sleep_end_short + '+00:00'
#print(sleep_end_short_UTC)
#granular_sleep_log=sleep_dict[0]['levels']
#print(granular_sleep_log)

#granular_sleep_log_dict=granular_sleep_log['data']
#print(granular_sleep_log_dict)

date_time_list=[]
sleep_state_list=[]

for i in sleep_dict[0]['levels']['data']:
    size=len(i['dateTime'])
    date_time_short = (i['dateTime'])[:size - 4]
    #date_time_short_UTC = (date_time_short.replace("T"," ")) + ' UTC'
    #date_time_short_UTC = date_time_short + '+00:00'
    date_time_list.append(date_time_short)
    sleep_state_list.append(i['level'])
date_time_list.append(sleep_end_short)
sleep_state_list.append(sleep_state_list[-1])
sleepdf = pd.DataFrame({'created_at':date_time_list,'field1':'',
                     'state_name':sleep_state_list})
sleepdf['field1'] = sleepdf['state_name'].map({'wake':'3','rem':'2','light':'1','deep':'0'})
#sleepdf=sleepdf.drop('state',axis=1)

sleep_csv=sleepdf.to_csv(('fitbit_sleep'+ today +'.csv'), index=False)

#########################################################################################

apiKey = 'REMOVED FOR PRIVACY' 

csvResults=""
with open(('fitbit_sleep'+ today +'.csv'), 'r') as readFile:
    reader = csv.DictReader(readFile)
    
    for row in reader: #for each row in the CSV
        print(row['created_at'], row['field1']) #See the rows in CSV file
        timestamp = row['created_at']
        sleepstate = row['field1']
        csvResults += (f"{timestamp}, {sleepstate}|") #This will append each row to a string
csvParams = urllib.parse.urlencode({'write_api_key': apiKey,'time_format': "absolute", 'updates': csvResults})
csvHeaders = {"Content-Type": "application/x-www-form-urlencoded"}
csvConn = http.client.HTTPConnection("api.thingspeak.com:80")
print("Attempting to write CSV to ThingSpeak")
csvConn.request("POST", "/channels/REMOVED/bulk_update.csv", csvParams, csvHeaders)
csvResponse = csvConn.getresponse()
print("Upload status: ", csvResponse.status, csvResponse.reason)
print("CSV upload successful!")