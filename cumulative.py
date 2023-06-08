import json
import time
import datetime

from config import *
import mysql.connector

mydb = mysql.connector.connect(user='root', password='admin', host='localhost', database='nic', auth_plugin='mysql_native_password')

def cumulative():
    # Read the initial value of 'flow' from data.json
    with open('data.json') as f:
     data = json.load(f)
     # Parse the JSON string in the "payload" field
     payload_dict = json.loads(data["payload"])
     # Read the value of the "flow" key
     flow_value = payload_dict["flow"]
     #print(flow_value)
     initial_flow = int(flow_value)
     #print(initial_flow)
     cumulative_value = int(initial_flow)
     #print(type(cumulative_value))
     #print(f"Initial flow value: {initial_flow}")

    # Read the updated values of 'flow' from data2.json for 60 times with 58 secoond interval
    for i in range(60):
     with open('LATEST_DATA.txt', 'r') as file:
        file_contents = file.read()
        # response = eval(file_contents)

        flow = int(file_contents[0:2])
        #print(type(flow))
        cumulative_value += flow
    time.sleep(59)
    #print(cumulative_value)
    # Store the calculated final value in a text file
    with open('final_cumulate_value.txt', 'w') as file:
        file.write(str(cumulative_value))
        # Get current timestamp
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    mycursor = mydb.cursor()
    sql = "INSERT INTO flow_hr_table(stn_id, plant_nm, device_id, flow, datetime) values (%s, %s, %s, %s, %s)"
    try:
        mycursor.execute(sql, (station_id, plant_nm, DEVICE_ID, cumulative_value, timestamp))
        mydb.commit()
        print(mycursor.rowcount, "details inserted")
    except Exception as e:
        print("Something went wrong:", e)

        mycursor.close()
        mydb.close()

    return cumulative_value


#print(cumulative())

cumulative()
