import time
from config import allocation

def calculated_allocation():
    consumption = 0
    with open('LATEST_RANDOM_DATA.txt', 'r') as file:
        file_contents = file.readlines()
    for line in file_contents:
        line = line.strip()# Remove leading/trailing whitespace
        #print(line)
        if line:
            line_data = line.split(',')
            if len(line_data) >= 1:
                try:
                    flow = float(line_data[0])
                    consumption += flow
                    extra_use = (allocation / 365) - consumption
                    #print(extra_use)
                    extra_use = max(extra_use, 0)  # Ensure extra_use is non-negative
                    print(flow)
                except ValueError:
                    print(f"Error: Unable to convert flow to float on line '{line}'")
            else:
                print(f"Error: Insufficient data on line '{line}'")
        else:
            print("Error: Empty line encountered")
    if extra_use > 0:
        extra_use = extra_use
    else:
        extra_use = 0
    print(consumption, extra_use)
    with open('cons&use_random.txt', 'w') as file:
        file.write(f'{round(consumption, 3)}, {extra_use}\n')
    time.sleep(59)

while True:
    calculated_allocation()
