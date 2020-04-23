from tkinter import Tk, ttk, Frame, Button, Label, Entry, Text, Checkbutton, \
    Scale, Listbox, Menu, BOTH, RIGHT, RAISED, N, E, S, W, simpledialog, \
    HORIZONTAL, END, FALSE, IntVar, StringVar, messagebox as box
from netmiko import ConnectHandler

class MIT_Tshooter(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.parent.title("Device Troubleshooter")
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.centreWindow()
        self.pack(fill=BOTH, expand=1)

##        menubar = Menu(self.parent)
##        self.parent.config(menu=menubar)
##        fileMenu = Menu(menubar)
##        fileMenu.add_command(label="Exit", command=self.quit)
##        menubar.add_cascade(label="File", menu=fileMenu)

        ipLabel = Label(self, text="Device IP")
        ipLabel.grid(row=0, column=0, sticky=W+E)
        usernameLabel = Label(self, text="Username")
        usernameLabel.grid(row=1, column=0, sticky=W+E)
        passwordLabel = Label(self, text="Password")
        passwordLabel.grid(row=2, column=0, sticky=W+E)
        devicemodelLabel = Label(self, text="Device Model")
        devicemodelLabel.grid(row=3, column=0, sticky=W+E)
        purposeLabel = Label(self, text="Purpose")
        purposeLabel.grid(row=4, column=0, sticky=W+E)

        self.ipVar = StringVar()
        ipText = Entry(self, width=20, textvariable=self.ipVar)
        ipText.grid(row=0, column=1, padx=5, pady=5, ipady=2, sticky=W+E)

        self.usernameVar = StringVar()
        usernameText = Entry(self, width=20, textvariable=self.usernameVar)
        usernameText.grid(row=1, column=1, padx=5, pady=5, ipady=2, sticky=W+E)

        self.passwordVar = StringVar()
        passwordText = Entry(self, width=20, show="*", textvariable=self.passwordVar)
        passwordText.grid(row=2, column=1, padx=5, pady=5, ipady=2, sticky=W+E)

        self.devicemodelVar = StringVar()
        self.devicemodelCombo = ttk.Combobox(self, textvariable=self.devicemodelVar)
        self.devicemodelCombo['values'] = ('cisco_ios',
                                           'cisco_asa',
                                           'cisco_nxos',
                                           'cisco_wlc',
                                           'cisco_s300',
                                           'cisco_xe',
                                           'cisco_xr',
                                           'fortinet')
        self.devicemodelCombo.current(0)
        #self.devicemodelCombo.bind("<<ComboboxSelected>>", self.newDeviceModel)
        self.devicemodelCombo.grid(row=3, column=1, padx=5, pady=5, ipady=2, sticky=W)

        self.purposeVar = StringVar()
        self.purposeCombo = ttk.Combobox(self, textvariable=self.purposeVar)
        self.purposeCombo['values'] = ('Basic Troubleshooting',
                                       'Performance Related',
                                       'Routing Related',
                                       'Hardening Related',
                                       'Custom...')
        self.purposeCombo.current(0)
        #self.purposeCombo.bind("<<ComboboxSelected>>", self.newPurpose)
        self.purposeCombo.grid(row=4, column=1, padx=5, pady=5, ipady=2, sticky=W)

        okBtn = Button(self, text="OK", width=10, command=self.onConfirm)
        okBtn.grid(row=5, column=0, padx=5, pady=3, sticky=W+E, columnspan=2)

    def centreWindow(self):
        w = 225
        h = 200
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def onConfirm(self):
        print(self.ipVar.get(),
              self.usernameVar.get(),
              self.passwordVar.get(),
              self.devicemodelVar.get(),
              self.purposeVar.get())
        if self.purposeVar.get() == 'Custom...':
            answer = simpledialog.askstring("Input", "What is your first name?",parent=self)
            print("Hooray!")
        else:
            print("not Hooray!")
        #box.showinfo("Information", "Thank you!")

def main():
    root = Tk()
    #root.geometry("250x150+300+300")    # width x height + x + y
    # we will use centreWindow instead
    root.resizable(width=FALSE, height=FALSE)
    # .. not resizable
    app = MIT_Tshooter(root)
    root.mainloop()

if __name__ == '__main__':
    main()
