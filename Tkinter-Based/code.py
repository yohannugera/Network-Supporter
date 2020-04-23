from tkinter import Tk, ttk, Frame, Button, Label, Entry, Text, Checkbutton, \
    Scale, Listbox, Menu, BOTH, RIGHT, RAISED, N, E, S, W, simpledialog, \
    HORIZONTAL, END, FALSE, IntVar, StringVar, messagebox as box, filedialog as fd
from netmiko import ConnectHandler

cisco_ios_Basic_Troubleshooting = ['show run',
                                   'show ip interface brief',
                                   'show interface description',
                                   'show version',
                                   'show cdp neighbors',
                                   'show process cpu history',
                                   'show clock'
                                   ]
cisco_ios_Performance_Related = ['show run | in hostname',
                                 'show interface',
                                 'show interface stats'
                                 ]
cisco_ios_Routing_Related = ['show ip route',
                             'show run | sec route'
                             ]
cisco_ios_Hardening_Related = ['show run',
                               'show interface description'
                               ]

def callback():
    name= fd.askopenfilename()
    print(name)

def netmiko_connection(device_ip, username, password, device_model, purpose):
    try:
        device = ConnectHandler(device_type=device_model,
                                ip=device_ip,
                                username=username,
                                password=password)
        logs_needed = globals()[device_model+'_'+'_'.join(purpose.split())]
        f = open("tshoot.log","a")
        for command in logs_needed:
            print("Now getting:",command)
            output = device.send_command(command)
            header_text = '----- Command: '+command+' -----'
            f.write('-'*len(header_text)+'\n')
            f.write(header_text+'\n')
            f.write('-'*len(header_text)+'\n')
            f.write('\n')
            f.write(output)
            f.write('\n')
        f.close()
        device.disconnect()
    except:
        print("Error occured")

form = Tk()
form.title("DevMon")
form.geometry("500x280")

tab_parent = ttk.Notebook(form)

tab1 = ttk.Frame(tab_parent)
tab2 = ttk.Frame(tab_parent)

tab_parent.add(tab1, text="Single Device")
tab_parent.add(tab2, text="Multiple Devices")

# === Widgets for Single Device ===

# Setting up Labels
device_ip_label = Label(tab1, text="Device IP:", justify="right")
username_label = Label(tab1, text="Username:", justify="right")
password_label = Label(tab1, text="Password:", justify="right")
device_model_label = Label(tab1, text="Device Model:", justify="right")
purpose_label = Label(tab1, text="Purpose:", justify="right")

# Setting up Device Spec. Placeholders
device_ip_var = StringVar(form)
username_var = StringVar(form)
password_var = StringVar(form)
device_model_var = StringVar(form)
purpose_var = StringVar(form)

# Setting up Entries
device_ip_entry = Entry(tab1,width=20,textvariable=device_ip_var)
username_entry = Entry(tab1,width=20,textvariable=username_var)
password_entry = Entry(tab1,width=20,textvariable=password_var,show="*")

# Setting up for device_model entry
device_model_entry = ttk.Combobox(tab1, textvariable=device_model_var)
device_model_entry['values'] = ('a10',
                                'cisco_asa',
                                'cisco_ios',
                                'cisco_nxos',
                                'cisco_s300',
                                'cisco_xe',
                                'cisco_tp',
                                'cisco_wlc',
                                'cisco_xr',
                                'fortinet'
                                )

device_model_entry.current(2) # set the default option

# Setting up for device_model entry
purpose_entry = ttk.Combobox(tab1, textvariable=purpose_var)
purpose_entry['values'] = ('Basic Troubleshooting',
                           'Performance Related',
                           'Routing Related',
                           'Hardening Related',
                           'Custom...'
                           )

purpose_entry.current(0) # set the default option

device_ip_label.grid(row=0, column=0, padx=5, pady=5, sticky=W+E)
device_ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky=W+E)

username_label.grid(row=1, column=0, padx=5, pady=5, sticky=W+E)
username_entry.grid(row=1, column=1, padx=5, pady=5, sticky=W+E)

password_label.grid(row=2, column=0, padx=5, pady=5, sticky=W+E)
password_entry.grid(row=2, column=1, padx=5, pady=5, sticky=W+E)

device_model_label.grid(row=3, column=0, padx=5, pady=5, sticky=W+E)
device_model_entry.grid(row=3, column=1, padx=5, pady=5, sticky=W)

purpose_label.grid(row=4, column=0, padx=5, pady=5, sticky=W+E)
purpose_entry.grid(row=4, column=1, padx=5, pady=5, sticky=W)

buttonOK = Button(tab1, text="Go!", command= lambda: netmiko_connection(device_ip_var.get(),
                                                                        username_var.get(),
                                                                        password_var.get(),
                                                                        device_model_var.get(),
                                                                        purpose_var.get()))
buttonOK.grid(row=5, column=0, padx=15, pady=15, sticky=W+E, columnspan=2)

# === Widgets for Multiple Devices ===
buttonFILE = Button(tab2, text='File Open',command=callback)
buttonFILE.grid(row=0, column=0, padx=15, pady=15, sticky=W+E, columnspan=2)
# Purpose of this widget to get multiple device details at once

tab_parent.pack(expand=1, fill='both')

# === Take Action
##from netmiko import ConnectHandler

form.mainloop()

## Supported Devices
##a10
##accedian
##alcatel_aos
##alcatel_sros
##apresia_aeos
##arista_eos
##aruba_os
##avaya_ers
##avaya_vsp
##brocade_fastiron
##brocade_netiron
##brocade_nos
##brocade_vdx
##brocade_vyos
##calix_b6
##checkpoint_gaia
##ciena_saos
##cisco_asa
##cisco_ios
##cisco_nxos
##cisco_s300
##cisco_tp
##cisco_wlc
##cisco_xe
##cisco_xr
##cloudgenix_ion
##coriant
##dell_dnos9
##dell_force10
##dell_isilon
##dell_os10
##dell_os6
##dell_os9
##dell_powerconnect
##eltex
##eltex_esr
##endace
##enterasys
##extreme
##extreme_ers
##extreme_exos
##extreme_netiron
##extreme_nos
##extreme_slx
##extreme_vdx
##extreme_vsp
##extreme_wing
##f5_linux
##f5_ltm
##f5_tmsh
##flexvnf
##fortinet
##generic_termserver
##hp_comware
##hp_procurve
##huawei
##huawei_vrpv8
##ipinfusion_ocnos
##juniper
##juniper_junos
##juniper_screenos
##keymile
##keymile_nos
##linux
##mellanox
##mellanox_mlnxos
##mikrotik_routeros
##mikrotik_switchos
##mrv_lx
##mrv_optiswitch
##netapp_cdot
##netscaler
##nokia_sros
##oneaccess_oneos
##ovs_linux
##paloalto_panos
##pluribus
##quanta_mesh
##rad_etx
##ruckus_fastiron
##ruijie_os
##ubiquiti_edge
##ubiquiti_edgeswitch
##vyatta_vyos
##vyos