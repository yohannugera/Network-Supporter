# This is the module to run the program execution

# User Input
# Device IP / Device Type / SSH or Telnet / Username and PW / Enable PW
#
#

import os
import extracting_module
import mon_functions

print("Welcome for Dev Mon 1.2 \n")
device_ip = str(input("Please Enter Device IP : "))
print("\n----------- Device Type ------------")
print("1. Cisco ios")
print("2. Other ")
device_type = int(input("Please Select a device type [1]/[2] : "))
print("\n------- Device Connection Type-------")
print("1. Telnet")
print("2. SSH")
device_protocol = int(input("Please Select a device type [1]/[2] : "))
print("\n--------User Authentication----------")
device_username = str(input("Enter Device Username : "))
device_pw = str(input("Enter Device Password : "))
device_secret = str(input("Enter Device Secret [leave blank if not set] :"))

# Default values loaded device dictionary
device = {
    'device_type': 'cisco_ios_telnet',
    'ip': '192.168.134.160',
    'username': 'mitsupport',
    'password': 'cisco',
    'secret': 'null',
    'port': '23'
}

# Modify device parameters with user input
device["ip"] = device_ip

if device_type == 1:
    if device_protocol == 1:
        device["device_type"] = "cisco_ios_telnet"
        device["port"] = "23"
    elif device_protocol == 2:
        device["device_type"] = "cisco_ios"
        device["port"] = "22"
    else:
        print("Invalid device details. Error !")
else:
    print("Only Cisco IOS devices are Supported at this time !")

device['username'] = device_username
device['password'] = device_pw
device['secret'] = device_secret

# Specify Purpose of user
print("\n--------Please Specify the Requirement---------")
print("1. Obtain Config-file and exit")
print("2. Obtain Common device details and exit")
print("3. Obtain Common device details, Config-file and exit")
print("4. Run a diagnostic session and exit [performance intensive]")
operation_selection = int(input("Please select an option [] : "))

# Confirmation of input
print("\n------Following will be used to login device -------")
print("dev_type : ", device['device_type'])
print("host ip  : ", device['ip'])
print("username : ", device['username'])
print("password : ", device['password'])
print("secret   : ", device['secret'])
print("port     : ", device['port'])
print("----------End Of Collected Data----------\n")

# Provide command execution nature to user
if operation_selection == 1:
    print("Device Running Config will be saved to local computer")
elif operation_selection == 2:
    print("Collected data will be saved in local computer")
elif operation_selection == 3:
    print("Collected data and device config will be saved in local computer")
elif operation_selection == 4:
    print("Collected data will be saved into local computer")
    print("DO NOT RUN THIS, DURING PRODUCTION HOURS !")

input("\nPress any key to continue ... ")
print("\nConnecting ... ")

# Executing Function on device
# Use Try Block

if operation_selection == 1:
    extracting_module.obtain_config(device)

elif operation_selection == 2:
    extracting_module.obtain_common_details(device)

elif operation_selection == 3:
    extracting_module.obtain_details_and_config(device)

elif operation_selection == 4:
    extracting_module.run_diagnostic_session(device)













