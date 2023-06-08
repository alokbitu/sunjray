import time
from config import allocation


def calculated_allocation():
    consuption = 0
    for i in range(1440):
     with open('LATEST_DATA.txt', 'r') as file:
        file_contents = file.read()
        flow = int(file_contents[0:2])
        print(flow)
     consuption += flow
     extra_use = (allocation/365) - consuption
     print(extra_use)
     if extra_use > 0:
        extra_use = extra_use
     else:
        extra_use = 0
    print(consuption,extra_use)
    with open('cons&use.txt','w') as file:
        file.write(f'{consuption}, {extra_use}\n')
    time.sleep(59)

while True:
    calculated_allocation()

#note:make a separate shell file for this py file and put the shell file in crontab as we did for comport program