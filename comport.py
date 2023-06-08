import datetime
import time
import random
import serial
import mysql.connector
from mysql.connector import errorcode
from config import *

mydb = mysql.connector.connect(user='root', password='admin', host='localhost', database='nic', auth_plugin='mysql_native_password')

counter = 0
total_flow = 0

def comport():
    global counter, total_flow
#serial communication code
    buf1 = ''
    # response = "+04.363+04.366+04.432+05.210+04.410+00.000+00.000+00.000"
    response = int( random.uniform(10, 30))
    print(response)

    # ser1 = serial.Serial(port=comport, baudrate=9600, timeout=2)
    # if not ser1.is_open:
    #     ser1.open()
    #     # print('serial Port1 Open for sending #01')
    #
    # ser1.flush()
    # ser1.flushInput()
    # ser1.flushOutput()
    # ser1.write(b'#01\r')
    # time.sleep(0.03)
    # response = ser1.readline().decode('ascii')
    # ser1.flush()
    # ser1.flushInput()
    # ser1.flushOutput()
    # ser1.close()
    # received_buffer = response
    # Get current timestamp
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    # for i in range(0, 6):
    #     buf1 = buf1 + received_buffer[i + 1]
    #
    # # convert string to float
    #     temp1 = float(buf1)
    # #print(temp1)
    # if temp1< MinMa or temp1>MaxMa:
    #     raw_value = 0
    # else:
    #     raw_value = temp1
    # temp_flow = raw_value
    # flow = (((temp_flow - MinMa) * maxAbs * multiplyFactors)/ (MaxMa - MinMa))
    # #print(round(flow,3))
    # counter =+ 1

# calculating average flow
    total_flow += response
    counter += 1
    avg_flow = total_flow / counter
    #print(round(avg_flow, 3))

    # Write to file with timestamp
    with open('DATA_RECORD.txt', 'a') as file1:
        file1.write(f'{response}, {timestamp}\n')

    # Write to file without timestamp (overwrite)
    with open('LATEST_DATA.txt', 'w') as file2:
        file2.write(f'{response}, {timestamp}\n')

    # calculating  min and max  flow
    Min = response
    Max = response
    if Min < response:
        Min = Min
    else:
        Min = response
    if Max > response:
        Max = Max
    else:
        Max = response
    #print(round(Min,3),round(Max,3))

    with open('cons&use.txt','r') as file3:
     file_contents = file3.read()
     consumption_str, extra_use_str = file_contents.split(', ')
     consumption = int(consumption_str)
     extra_use = int(extra_use_str)
     #print(file_contents)


    mycursor = mydb.cursor()
    sql = "INSERT INTO flow_minute_table(stn_id, plant_nm, device_id, flow,min_flow,max_flow,allocation,consumption,extra_use,avg_flow, datetime) values (%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        mycursor.execute(sql,(station_id,plant_nm,DEVICE_ID,response,Min,Max,allocation,consumption,extra_use,round(avg_flow,3),timestamp))
        mydb.commit()
        print(mycursor.rowcount, "details inserted")
    except Exception as e:
        print("Something went wrong:", e)

        mycursor.close()
        mydb.close()


if __name__ == '__main__':
    while True:
        comport()
        time.sleep(60)