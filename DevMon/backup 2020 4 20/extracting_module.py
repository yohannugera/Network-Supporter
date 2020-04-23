# This module is written to extract data from Cisco Devices.
# Device configuration should be passed down to here.
# Use cases are defiled as functions. Adding or removing them can be done


import os
import mon_functions
import processing_module
from netmiko import ConnectHandler
from netmiko import BaseConnection


# Case 1: Obtain Config-file and exit
def obtain_config(device):
    # Establish Connection here, and terminate afterwards
    try:
        connection = ConnectHandler(**device)
        connection.enable()
        #mon_functions.get_device_config()
        dev_interfaces = mon_functions.get_device_interface_brief(connection)

        print("\n\n----------------Interface Details---------------------\n")
        print(dev_interfaces)

        connection.disconnect()

    except Exception as ex:
        print("Error While Establishing Connection !")
        print("Detailed Error : ", ex)


# Case 2: Obtain Common device details and exit

def obtain_common_details(device):
    # Establish Connection here, and terminate afterwards
    try:
        connection = ConnectHandler(**device)
        connection.enable()

        # Obtain device details
        dev_hostname = mon_functions.get_device_hostname(connection)
        dev_clock = mon_functions.get_device_clock(connection)
        dev_uptime = mon_functions.get_device_uptime(connection)
        dev_ios = mon_functions.get_device_firmware_version(connection)
        dev_serial = mon_functions.get_device_serial_number(connection)
        dev_model = mon_functions.get_device_model_number(connection)
        dev_cdpneighbours = mon_functions.get_device_cdp_neighbors(connection)
        dev_interfaces = mon_functions.get_device_interface_brief(connection)
        dev_intdescriptions = mon_functions.get_device_interface_description(connection)
        dev_cpuhistory = mon_functions.get_device_cpu_history(connection)

        connection.disconnect()

    except Exception as ex:
        print("Error While Establishing Connection :")
        print("Detailed Error : ", ex)

    # Print Information for the Output
    os.system('cls')
    processing_module.print_header()
    processing_module.print_dev_hostname(dev_hostname, device["ip"])
    processing_module.print_detail('Device Time', dev_clock)
    processing_module.print_detail('Device Up-time', dev_uptime)
    processing_module.print_detail('Device Firmware', dev_ios)
    processing_module.print_detail('Device Serial', dev_serial)
    processing_module.print_detail('Device Model', dev_model)
    processing_module.print_section_detail('Interface Status', dev_interfaces)
    processing_module.print_section_detail('Interface Descriptions', dev_intdescriptions)
    processing_module.print_section_detail('CDP Neighbors', dev_cdpneighbours)
    processing_module.print_section_detail('CPU History', dev_cpuhistory)


# Case 3: Obtain Common device details, Config-file and exit

def obtain_details_and_config(device):
    # Establish Connection here, and terminate afterwards
    try:
        connection = ConnectHandler(**device)
        connection.enable()

        mon_functions.get_device_interface_brief(connection)
        mon_functions.get_device_interface_description(connection)
        mon_functions.get_device_uptime(connection)
        mon_functions.get_device_firmware_version(connection)
        mon_functions.get_device_cdp_neighbors(connection)
        mon_functions.get_device_hostname(connection)
        mon_functions.get_device_clock(connection)
        mon_functions.get_device_cpu_history(connection)
        mon_functions.get_device_serial_number(connection)
        mon_functions.get_device_config(connection)

    except Exception as ex:
        print("Error While Establishing Connection :")
        print("Detailed Error : ", ex)

# Case 4: Run a diagnostic session and exit [performance intensive]
def run_diagnostic_session(device):
    # Establish Connection here, and terminate afterwards
    try:
        connection = ConnectHandler(**device)
        connection.enable()

        mon_functions.get_device_interface_brief(connection)
        mon_functions.get_device_interface_description(connection)
        mon_functions.get_device_uptime(connection)
        mon_functions.get_device_firmware_version(connection)
        mon_functions.get_device_cdp_neighbors(connection)
        mon_functions.get_device_hostname(connection)
        mon_functions.get_device_clock(connection)
        mon_functions.get_device_cpu_history(connection)
        mon_functions.get_device_serial_number(connection)
        mon_functions.get_device_config(connection)
        mon_functions.get_device_showtech(connection)
        connection.disconnect()

    except Exception as ex:
        print("Error While Establishing Connection :")
        print("Detailed Error : ", ex)