import netmiko
import os
from netmiko import ConnectHandler

#Connect
switch = {
    'device_type': 'cisco_ios_telnet',
    'ip': '192.168.134.160',
    'username': 'mitsupport',
    'password': 'cisco',
    'secret': 'cisco',
    'port': '23'
    }

try:
    connect = ConnectHandler(**switch)
    connect.enable()
    interfaces = connect.send_command('sh ip int brief')
    intdescriptions = connect.send_command('sh interface description')
    deviceuptime = connect.send_command('sh version | in uptime')
    deviceios = connect.send_command('sh version | in ios')
    cdpneighbours = connect.send_command('sh cdp neighbors | b Device ID')
    hostname = connect.send_command('sh run | in hostname')
    deviceclock = connect.send_command('sh clock')
    devicecpu = connect.send_command('sh process cpu history')
    

    os.system('clear')
    print("------------------------------------------\n")
    print("DevMon V 1.1 - Cisco Router/Switch details \n")
    print("------------------------------------------\n\n")

    print("Device " + hostname + " | IP : ", switch["ip"])
    print("\n\n----------------Device Time---------------------------\n")
    print(deviceclock)
    print("\n\n----------------Interface Details---------------------\n")
    print(interfaces)
    print("\n\n--------------Interface Descriptions------------------\n")
    print(intdescriptions)
    print("\n\n------------------Device Up-Time----------------------\n")
    print(deviceuptime)
    print("\n\n---------------------Firmware Version-------------------\n")
    print(deviceios)
    print("\n\n-----------------------Device Neighbors-----------------\n")
    print(cdpneighbours)
    print("\n\n------------------------CPU History---------------------\n")
    print(devicecpu)

    connect.disconnect()
except Exception as exe:
    print('Error Here !!!!! !')
    print(exe)
