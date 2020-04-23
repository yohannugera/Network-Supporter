# This module is responsible of printing output
# This also contains file writing modules

import os

def print_header():
    # Prints the Header of Output
    print("\n-----------------------------------------")
    print("DevMon V 1.2 - Cisco Router/Switch details ")
    print("-------------------------------------------\n")

def print_detail(dheader, dev_detail):
    # Prints details of device
    print(str(dheader), "   :  ", dev_detail)

def print_section_detail(dheader, dev_detail):
    # prints details in sections
    print("\n---------------------------------", dheader, "---------------------------------")
    print(dev_detail)
    print("-------------------------------------------------------------------------------\n")

def print_dev_hostname(dev_hostname, dev_ip):
    # Prints device hostname
    print("Device ", dev_hostname )
    print("Host IP  :   ", dev_ip)

