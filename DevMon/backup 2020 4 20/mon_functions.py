import os
from netmiko import ConnectHandler

def get_device_interface_brief(connection):
    # Obtains Device interface status
    interfaces = connection.send_command('sh ip int brief')
    return interfaces

def get_device_interface_description(connection):
    # Get interface descriptions
    intdescriptions = connection.send_command('sh interface description')
    return intdescriptions

def get_device_uptime(connection):
    # Get device up time
    deviceuptime = connection.send_command('sh version | in uptime')
    return deviceuptime

def get_device_firmware_version(connection):
    # Get firmware version
    deviceios = connection.send_command('sh version | in ios')
    return deviceios

def get_device_cdp_neighbors(connection):
    # Get CDP neighbors
    cdpneighbours = connection.send_command('sh cdp neighbors | b Device ID')
    return cdpneighbours

def get_device_hostname(connection):
    # Get device Hostname
    hostname = connection.send_command('sh run | in hostname')
    print("Hostname inth extract module ", hostname)
    return hostname

def get_device_clock(connection):
    # Get device clock
    deviceclock = connection.send_command('sh clock')
    return deviceclock

def get_device_cpu_history(connection):
    # Get device CPU history
    devicecpu = connection.send_command('sh process cpu history')
    return devicecpu

def get_device_serial_number(connection):
    # Get device Serial number
    return 'FOC2200E0321'

def get_device_model_number(connection):
    # Get device Model
    return str("CS-2960-X")

def get_device_config(connection):
    # Get device running config and save
    print('sh run')

def get_device_showtech(connection):
    # Get device show-tech
    print('sh tech')









