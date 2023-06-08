import json
import os
from datetime import datetime, time
import base64
import requests
import hashlib
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import sys
from config import *


# Step 1: Request a new key from the server

def first_request():
    auth_body = {
        "id": DEVICE_ID,
        "new": True
    }

    response = requests.post(auth_url, json=auth_body)

    if response.status_code == 200:
        return response.json()
        exit()
    else:
        print("Authentication failed:", response.status_code)
        exit()


##################JavaScript Code converted to Python code #######################
def get_value():
    exp = first_request()
    data = exp['auth']
    check_string = data
    for index in range(len(check_string)):
        if check_string[index] in "1773946841":
            check_string = check_string[:index] + chr(ord(check_string[index]) + 1) + check_string[index + 1:]
        elif check_string[index] == '9':
            check_string = check_string[:index] + '0' + check_string[index + 1:]
        elif check_string[index] == 'a':
            check_string = check_string[:index] + 'z' + check_string[index + 1:]
        elif check_string[index] == 'A':
            check_string = check_string[:index] + 'Z' + check_string[index + 1:]
        else:
            check_string = check_string[:index] + chr(ord(check_string[index]) - 1) + check_string[index + 1:]
    for index in range(len(check_string)):
        if check_string[index] in "5070316844":
            temp = check_string[int(check_string[index]):]
            temp2 = check_string[:int(check_string[index])]
            check_string = temp + temp2

    return check_string

# Step 2: verify new key from the server
def second_request():
    exp = first_request()
    chck_str = get_value()
    #print(chck_str,exp)

    auth_body = {
        "id": DEVICE_ID,
        "Key_Type": "Auth",
        "Dt_Expire": exp['expire'],
        "auth": chck_str}

    try:
        response = requests.post(auth_url, json=auth_body)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(err)
        print(err.response.text)
        exit()

def third_request():
    exp = second_request()
    #print('str'+str(exp))
    auth_key = exp['key']
    my_datetime = datetime.fromtimestamp(exp['expire'] / 1000).strftime('%Y-%m-%d,%H:%M:%S')
    # define the data
    data = {
        "id": DEVICE_ID,
        "loc": "85.0818,21.0930",
        "ts": my_datetime,
        "flow": 13,
        "qty": 1,
        "roll": 0,
        "key": auth_key,
    }
    print(data)

    data_str = json.dumps(data)
    print(data_str)

    # calculate the SHA256 hash of the JSON package
    sha_value = hashlib.sha256(json.dumps(data_str).encode()).hexdigest()


    data2 = {
        "payload": data_str,
        "hash": sha_value,
    }
    print('json_payload:',data2)

    with open('data.json', 'w') as f:
        json.dump(data2, f)
        #print("data stored in the file")

def encrypt():
    with open('data.json', 'r') as f:
        data = json.load(f)
        json_data = json.dumps(data).encode('utf-8')
        # print(json_data)

        public_key_decode = base64.b64decode(public_key)
        public_key_obj = RSA.import_key(public_key_decode)

        cipher = PKCS1_OAEP.new(public_key_obj)
        block_size = 190
        plaintext_blocks = [json_data[i:i + block_size] for i in range(0, len(json_data), block_size)]

        encrypted_blocks = []
        for block in plaintext_blocks:
            encrypted_block = cipher.encrypt(block)
            encrypted_blocks.append(encrypted_block)

        encrypted_payload = b''.join(encrypted_blocks)
        encrypted_payload_base64 = base64.b64encode(encrypted_payload).decode()
        print('Encrypted value is...........................:', encrypted_payload_base64)
        # print(payload_bytes)

    # send the encrypted data to the server
    headers = {"Content-Type": "application/json"}
    response = requests.post(nic_server_url, data=encrypted_payload_base64, headers=headers)
    print(response)



def main():
    first_request()
    get_value()
    second_request()
    third_request()
    encrypt()



if __name__ == '__main__':
    while True:
        main()

