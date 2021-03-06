from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp
import time
import traceback
from netmiko import ConnectHandler
import logging
import pandas as pd
import re

logging.basicConfig(level=logging.DEBUG,
                    filename='app.log',
                    filemode='w',
                    format='%(asctime)s - %(message)s')

class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(str)
class Worker(QtCore.QRunnable):
    def __init__(self, fn, ip, username, password, model, *commands, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.ip = ip
        self.username = username
        self.password = password
        self.model = model
        self.commands = commands
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress
    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.fn(self.ip,
                             self.username,
                             self.password,
                             self.model,
                             *self.commands,
                             **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class Multiple_Device_WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(str)
class Multiple_Device_Worker(QtCore.QRunnable):
    def __init__(self, fn, *devices_list, **kwargs):
        super(Multiple_Device_Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.devices_list = devices_list
        self.kwargs = kwargs
        self.signals = Multiple_Device_WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress
    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.devices_list,
                             **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class Ui_MainWindow(QtWidgets.QWidget):
    # Local Variables and Hardening Stuff...
    threadpool = QtCore.QThreadPool()
    multiple_threadpool = QtCore.QThreadPool()
    ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"  # Part of the regular expression
    ipRegex = QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")
    ipValidator = QtGui.QRegExpValidator(ipRegex)
    fullIPregex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    models = ['cisco_ios','cisco_asa','fortinet']
    purpose = ['Basic Troubleshooting','Performance Related']
    selected_file = ""
    popup_notification = "Process Started..."
    options = {'Basic Troubleshooting':'BT', 'Performance Related':'PR'}
    cisco_ios_BT = ["show run"]
    cisco_ios_PR = ["show run"]
    cisco_asa_BT = ["show run"]
    cisco_asa_PR = ["show run"]
    fortinet_BT = ["show"]
    fortinet_PR = ["show"]

    # Button functions
    def go_ssh_button_clicked(self):
        ssh_ip = self.device_ip_entry.text()
        ssh_username = self.username_ssh_entry.text()
        ssh_password = self.password_ssh_entry.text()
        ssh_model = self.model_ssh_combobox.currentText()
        ssh_purpose = self.purpose_ssh_combobox.currentText()
        commands_to_taken = eval('self.'+ssh_model+"_"+self.options[ssh_purpose])
        if (ssh_ip=="") or (ssh_username=="") or (ssh_password==""):
            self.caution_msg()
        else:
            logging.info("Log collection for single device via SSH started.")
            self.get_logs(ssh_ip, ssh_username, ssh_password, ssh_model, *commands_to_taken)
    def go_console_button_clicked(self):
        baud_rate = self.baud_rate_console_entry.text()
        com_port = self.com_port_console_entry.text()
        username = self.username_console_entry.text()
        password = self.password_console_entry.text()
        enable_secret = self.enable_console_entry.text()
        model = self.model_console_combobox.currentText()
        purpose = self.purpose_console_combobox.currentText()
        self.not_coded_msg()
    def add_row_button_clicked(self):
        rowPosition = self.manual_device_table.rowCount()
        self.manual_device_table.insertRow(rowPosition)
        #cell_mask = QtWidgets.QLineEdit.setEchoMode()
        #self.manual_device_table.setCellWidget(rowPosition, 2, cell_mask)
        model_combo = QtWidgets.QComboBox()
        for t in self.models:
            model_combo.addItem(t)
        model_combo.setCurrentIndex(0)
        self.manual_device_table.setCellWidget(rowPosition, 3, model_combo)
        purpose_combo = QtWidgets.QComboBox()
        for t in self.purpose:
            purpose_combo.addItem(t)
        purpose_combo.setCurrentIndex(0)
        self.manual_device_table.setCellWidget(rowPosition, 4, purpose_combo)
        self.manual_device_table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
    def delete_row_button_clicked(self):
        indices = self.manual_device_table.selectionModel().selectedRows()
        for index in sorted(indices):
            self.manual_device_table.removeRow(index.row())
    def go_manual_button_clicked(self):
        manual_devices = []
        for entry in range(self.manual_device_table.rowCount()):
            manual_ip = self.manual_device_table.item(entry,0).text()
            manual_username = self.manual_device_table.item(entry,1).text()
            manual_password = self.manual_device_table.item(entry, 2).text()
            manual_model = self.manual_device_table.cellWidget(entry, 3).currentText()
            manual_purpose = self.manual_device_table.cellWidget(entry, 4).currentText()
            commands_to_taken = eval('self.'+manual_model+"_"+self.options[manual_purpose])
            if (manual_ip == "") or (manual_username == "") or (manual_password == ""):
                self.caution_msg()
            else:
                manual_devices.append((manual_ip,manual_username,manual_password,manual_model,manual_purpose))
        self.get_multiple_device_logs(*manual_devices)
    def get_file_button_clicked(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                      "", "CSV files (*.csv)")
        self.selected_file = file_name[0]
        self.get_file_button.setText(self.selected_file)
    def go_file_button_clicked(self):
        self.devices_data = pd.read_csv(self.selected_file)
        self.devices_list = []

        for index, row in self.devices_data.iterrows():
            self.devices_list.append((row['ip'], row['username'], row['password'], row['model'], row['purpose']))

        devices = []
        for entry in self.devices_list:
            ip = entry[0]
            username = entry[1]
            password = entry[2]
            model = entry[3]
            purpose = entry[4]
            if (ip == "") or (username == "") or (password == ""):
                self.caution_msg()
            else:
                devices.append((ip,username,password,model,purpose))
        self.get_multiple_device_logs(*devices)

    # Connect to device...
    def connect_device(self, ip, username, password, model, *commands, progress_callback):
        device = ConnectHandler(device_type=model,
                                ip=ip,
                                username=username,
                                password=password)
        progress_callback.emit("Connected to "+ip)
        f = open("tshoot.log", "w")
        for command in commands[0]:
            print(commands)
            progress_callback.emit("Getting output of \""+command+"\"")
            output = device.send_command(command)
            header_text = 'command: ' + command
            f.write(header_text + '\n')
            f.write('output: '+'\n')
            f.write(output)
        f.close()
        device.disconnect()
        return("Log Collection for "+ip+" done.")
    def multiple_connect_device(self, *devices_list, progress_callback):
        for entry in devices_list[0]:
            if re.match(self.fullIPregex,entry[0]):
                device = ConnectHandler(device_type=entry[3],
                                        ip=entry[0],
                                        username=entry[1],
                                        password=entry[2])
                progress_callback.emit("Connected to "+entry[0])
                f = open(entry[0]+"_"+entry[3]+"_"+self.options[entry[4]]+"("+str(time.localtime().tm_year)+"-"+str(time.localtime().tm_mon)+"-"+str(time.localtime().tm_mday)+"-"+str(time.localtime().tm_hour)+"-"+str(time.localtime().tm_min)+"-"+str(time.localtime().tm_sec)+").log","w")
                for command in eval('self.'+entry[3]+"_"+self.options[entry[4]]):
                    progress_callback.emit("Getting output of \""+command+"\"")
                    output = device.send_command(command)
                    header_text = 'command: ' + command
                    f.write(header_text + '\n')
                    f.write('output: '+'\n')
                    f.write(output)
                f.close()
                device.disconnect()
                progress_callback.emit("Log Collection for "+entry[0]+" done.")
            else:
                progress_callback.emit("Please enter valid IP.")
                pass
        return("Log Collection done.")
    def tmp_connect_device(self, ip, username, password, model, *commands, progress_callback):
        # After GUI testing is done. Replace this by connect_device...
        progress_callback.emit("Connected to "+ip)
        for command in commands[0]:
            progress_callback.emit("Getting output of \""+command+"\"")
            time.sleep(5)
        return("Log Collection for "+ip+" done.")
    def tmp_multiple_connect_device(self, *devices_list, progress_callback):
        # After GUI testing is done. Replace this by connect_device...
        for device in devices_list[0]:
            progress_callback.emit("Connected to " + str(device[0]))
            progress_callback.emit("Getting output for \""+str(device[0])+"\"")
            time.sleep(5)
        return("Log Collection for all devices done.")

    # Multitasking log collection...
    def get_logs(self, ip, username, password, model, *commands):
        # Create a new thread and pass the process to it
        worker = Worker(self.tmp_connect_device,
                        ip,
                        username,
                        password,
                        model,
                        commands)
        worker.signals.result.connect(self.finish_popup_msg)
        worker.signals.finished.connect(self.finish_thread_msg)
        worker.signals.progress.connect(self.change_popup_msg)
        # Execute
        self.threadpool.start(worker)
        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle("Status")
        self.msg.setText("Information Gathering in progress...")
        self.msg.setIcon(QtWidgets.QMessageBox.Question)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        self.msg.setDetailedText(self.popup_notification)
        self.msg.show()
    def get_multiple_device_logs(self, *devices_list):
        # Create a new thread and pass the process to it
        worker = Multiple_Device_Worker(self.multiple_connect_device, devices_list)
        worker.signals.result.connect(self.finish_popup_msg)
        worker.signals.finished.connect(self.finish_thread_msg)
        worker.signals.progress.connect(self.change_popup_msg)
        # Execute
        self.multiple_threadpool.start(worker)
        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle("Status")
        self.msg.setText("Information Gathering in progress...")
        self.msg.setIcon(QtWidgets.QMessageBox.Question)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        self.msg.setDetailedText(self.popup_notification)
        self.msg.show()
    def change_popup_msg(self, n):
        self.popup_notification = self.popup_notification + "\n" + n
        self.msg.setDetailedText(self.popup_notification)
    def finish_popup_msg(self, s):
        self.popup_notification = self.popup_notification + "\n" + s
        self.msg.setDetailedText(self.popup_notification)
    def finish_thread_msg(self):
        self.popup_notification = self.popup_notification + "\n" + "Process finished!"
        self.msg.setDetailedText(self.popup_notification)

    # Warning for user to enter all necessary information...
    def caution_msg(self):
        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle("Caution")
        self.msg.setText("Please input all information...")
        self.msg.setIcon(QtWidgets.QMessageBox.Warning)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        self.msg.show()
    def not_coded_msg(self):
        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle("Sorry")
        self.msg.setText("This feature is not implemented yet...")
        self.msg.setIcon(QtWidgets.QMessageBox.Warning)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Close)
        self.msg.show()

    # Qt Designer Generated
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 400)
        MainWindow.setMaximumSize(QtCore.QSize(500, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.single_device_tab = QtWidgets.QWidget()
        self.single_device_tab.setObjectName("single_device_tab")
        self.single_device_toolbox = QtWidgets.QToolBox(self.single_device_tab)
        self.single_device_toolbox.setGeometry(QtCore.QRect(10, 10, 461, 341))
        self.single_device_toolbox.setObjectName("single_device_toolbox")
        self.via_ssh_page = QtWidgets.QWidget()
        self.via_ssh_page.setGeometry(QtCore.QRect(0, 0, 461, 297))
        self.via_ssh_page.setObjectName("via_ssh_page")
        self.device_ip = QtWidgets.QLabel(self.via_ssh_page)
        self.device_ip.setGeometry(QtCore.QRect(100, 10, 81, 21))
        self.device_ip.setTextFormat(QtCore.Qt.RichText)
        self.device_ip.setObjectName("device_ip")
        self.device_ip_entry = QtWidgets.QLineEdit(self.via_ssh_page)
        self.device_ip_entry.setGeometry(QtCore.QRect(190, 10, 131, 21))
        self.device_ip_entry.setObjectName("device_ip_entry")
        self.model_ssh_combobox = QtWidgets.QComboBox(self.via_ssh_page)
        self.model_ssh_combobox.setGeometry(QtCore.QRect(190, 100, 131, 21))
        self.model_ssh_combobox.setObjectName("model_ssh_combobox")
        self.model_ssh_combobox.addItem("")
        self.model_ssh_combobox.addItem("")
        self.model_ssh_combobox.addItem("")
        self.username_ssh = QtWidgets.QLabel(self.via_ssh_page)
        self.username_ssh.setGeometry(QtCore.QRect(100, 40, 81, 21))
        self.username_ssh.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.username_ssh.setTextFormat(QtCore.Qt.RichText)
        self.username_ssh.setObjectName("username_ssh")
        self.username_ssh_entry = QtWidgets.QLineEdit(self.via_ssh_page)
        self.username_ssh_entry.setGeometry(QtCore.QRect(190, 40, 131, 21))
        self.username_ssh_entry.setObjectName("username_ssh_entry")
        self.password_ssh_entry = QtWidgets.QLineEdit(self.via_ssh_page)
        self.password_ssh_entry.setGeometry(QtCore.QRect(190, 70, 131, 21))
        self.password_ssh_entry.setObjectName("password_ssh_entry")
        self.password_ssh = QtWidgets.QLabel(self.via_ssh_page)
        self.password_ssh.setGeometry(QtCore.QRect(100, 70, 81, 21))
        self.password_ssh.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.password_ssh.setTextFormat(QtCore.Qt.RichText)
        self.password_ssh.setObjectName("password_ssh")
        self.model_ssh = QtWidgets.QLabel(self.via_ssh_page)
        self.model_ssh.setGeometry(QtCore.QRect(100, 100, 81, 21))
        self.model_ssh.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.model_ssh.setTextFormat(QtCore.Qt.RichText)
        self.model_ssh.setObjectName("model_ssh")
        self.purpose_ssh_combobox = QtWidgets.QComboBox(self.via_ssh_page)
        self.purpose_ssh_combobox.setGeometry(QtCore.QRect(190, 130, 131, 21))
        self.purpose_ssh_combobox.setObjectName("purpose_ssh_combobox")
        self.purpose_ssh_combobox.addItem("")
        self.purpose_ssh = QtWidgets.QLabel(self.via_ssh_page)
        self.purpose_ssh.setGeometry(QtCore.QRect(100, 130, 81, 21))
        self.purpose_ssh.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.purpose_ssh.setTextFormat(QtCore.Qt.RichText)
        self.purpose_ssh.setObjectName("purpose_ssh")
        self.go_ssh_button = QtWidgets.QPushButton(self.via_ssh_page)
        self.go_ssh_button.setGeometry(QtCore.QRect(190, 160, 131, 21))
        self.go_ssh_button.setObjectName("go_ssh_button")
        self.single_device_toolbox.addItem(self.via_ssh_page, "")
        self.via_console_page = QtWidgets.QWidget()
        self.via_console_page.setGeometry(QtCore.QRect(0, 0, 461, 297))
        self.via_console_page.setObjectName("via_console_page")
        self.purpose_console = QtWidgets.QLabel(self.via_console_page)
        self.purpose_console.setGeometry(QtCore.QRect(90, 190, 91, 21))
        self.purpose_console.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.purpose_console.setTextFormat(QtCore.Qt.RichText)
        self.purpose_console.setObjectName("purpose_console")
        self.baud_rate = QtWidgets.QLabel(self.via_console_page)
        self.baud_rate.setGeometry(QtCore.QRect(90, 10, 91, 21))
        self.baud_rate.setTextFormat(QtCore.Qt.RichText)
        self.baud_rate.setObjectName("baud_rate")
        self.username_console_entry = QtWidgets.QLineEdit(self.via_console_page)
        self.username_console_entry.setGeometry(QtCore.QRect(190, 70, 131, 20))
        self.username_console_entry.setObjectName("username_console_entry")
        self.com_port_console_entry = QtWidgets.QLineEdit(self.via_console_page)
        self.com_port_console_entry.setGeometry(QtCore.QRect(190, 40, 131, 20))
        self.com_port_console_entry.setObjectName("com_port_console_entry")
        self.com_port = QtWidgets.QLabel(self.via_console_page)
        self.com_port.setGeometry(QtCore.QRect(90, 40, 91, 21))
        self.com_port.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.com_port.setTextFormat(QtCore.Qt.RichText)
        self.com_port.setObjectName("com_port")
        self.model_console_combobox = QtWidgets.QComboBox(self.via_console_page)
        self.model_console_combobox.setGeometry(QtCore.QRect(190, 160, 131, 22))
        self.model_console_combobox.setObjectName("model_console_combobox")
        self.model_console_combobox.addItem("")
        self.model_console_combobox.addItem("")
        self.model_console_combobox.addItem("")
        self.go_console_button = QtWidgets.QPushButton(self.via_console_page)
        self.go_console_button.setGeometry(QtCore.QRect(190, 220, 131, 21))
        self.go_console_button.setObjectName("go_console_button")
        self.purpose_console_combobox = QtWidgets.QComboBox(self.via_console_page)
        self.purpose_console_combobox.setGeometry(QtCore.QRect(190, 190, 131, 22))
        self.purpose_console_combobox.setObjectName("purpose_console_combobox")
        self.purpose_console_combobox.addItem("")
        self.baud_rate_console_entry = QtWidgets.QLineEdit(self.via_console_page)
        self.baud_rate_console_entry.setGeometry(QtCore.QRect(190, 10, 131, 20))
        self.baud_rate_console_entry.setObjectName("baud_rate_console_entry")
        self.model_console = QtWidgets.QLabel(self.via_console_page)
        self.model_console.setGeometry(QtCore.QRect(90, 160, 91, 21))
        self.model_console.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.model_console.setTextFormat(QtCore.Qt.RichText)
        self.model_console.setObjectName("model_console")
        self.username_console = QtWidgets.QLabel(self.via_console_page)
        self.username_console.setGeometry(QtCore.QRect(90, 70, 91, 21))
        self.username_console.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.username_console.setTextFormat(QtCore.Qt.RichText)
        self.username_console.setObjectName("username_console")
        self.password_console = QtWidgets.QLabel(self.via_console_page)
        self.password_console.setGeometry(QtCore.QRect(90, 100, 91, 21))
        self.password_console.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.password_console.setTextFormat(QtCore.Qt.RichText)
        self.password_console.setObjectName("password_console")
        self.password_console_entry = QtWidgets.QLineEdit(self.via_console_page)
        self.password_console_entry.setGeometry(QtCore.QRect(190, 100, 131, 20))
        self.password_console_entry.setObjectName("password_console_entry")
        self.enable_console_entry = QtWidgets.QLineEdit(self.via_console_page)
        self.enable_console_entry.setGeometry(QtCore.QRect(190, 130, 131, 20))
        self.enable_console_entry.setObjectName("enable_console_entry")
        self.enable_console = QtWidgets.QLabel(self.via_console_page)
        self.enable_console.setGeometry(QtCore.QRect(90, 130, 91, 21))
        self.enable_console.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.enable_console.setTextFormat(QtCore.Qt.RichText)
        self.enable_console.setObjectName("enable_console")
        self.single_device_toolbox.addItem(self.via_console_page, "")
        self.tabWidget.addTab(self.single_device_tab, "")
        self.multiple_device_tab = QtWidgets.QWidget()
        self.multiple_device_tab.setObjectName("multiple_device_tab")
        self.multiple_device_toolbox = QtWidgets.QToolBox(self.multiple_device_tab)
        self.multiple_device_toolbox.setGeometry(QtCore.QRect(10, 10, 461, 341))
        self.multiple_device_toolbox.setObjectName("multiple_device_toolbox")
        self.manual_add_page = QtWidgets.QWidget()
        self.manual_add_page.setGeometry(QtCore.QRect(0, 0, 461, 297))
        self.manual_add_page.setObjectName("manual_add_page")
        self.manual_device_table = QtWidgets.QTableWidget(self.manual_add_page)
        self.manual_device_table.setGeometry(QtCore.QRect(10, 10, 441, 241))
        self.manual_device_table.setObjectName("manual_device_table")
        self.manual_device_table.setColumnCount(5)
        self.manual_device_table.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.manual_device_table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.manual_device_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.manual_device_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.manual_device_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.manual_device_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.manual_device_table.setHorizontalHeaderItem(4, item)
        self.manual_device_table.horizontalHeader().setSortIndicatorShown(False)
        self.add_row_button = QtWidgets.QPushButton(self.manual_add_page)
        self.add_row_button.setGeometry(QtCore.QRect(10, 260, 21, 21))
        self.add_row_button.setObjectName("add_row_button")
        self.delete_row_button = QtWidgets.QPushButton(self.manual_add_page)
        self.delete_row_button.setGeometry(QtCore.QRect(40, 260, 21, 21))
        self.delete_row_button.setObjectName("delete_row_button")
        self.go_manual_button = QtWidgets.QPushButton(self.manual_add_page)
        self.go_manual_button.setGeometry(QtCore.QRect(390, 260, 61, 21))
        self.go_manual_button.setObjectName("go_manual_button")
        self.multiple_device_toolbox.addItem(self.manual_add_page, "")
        self.file_add_page = QtWidgets.QWidget()
        self.file_add_page.setGeometry(QtCore.QRect(0, 0, 461, 297))
        self.file_add_page.setObjectName("file_add_page")
        self.go_file_button = QtWidgets.QPushButton(self.file_add_page)
        self.go_file_button.setGeometry(QtCore.QRect(390, 10, 61, 21))
        self.go_file_button.setObjectName("go_file_button")
        self.get_file_button = QtWidgets.QPushButton(self.file_add_page)
        self.get_file_button.setGeometry(QtCore.QRect(10, 10, 371, 21))
        self.get_file_button.setObjectName("get_file_button")
        self.multiple_device_toolbox.addItem(self.file_add_page, "")
        self.tabWidget.addTab(self.multiple_device_tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.single_device_toolbox.setCurrentIndex(0)
        self.multiple_device_toolbox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Network-Supporter"))
        self.device_ip.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Device IP: </span></p></body></html>"))
        self.model_ssh_combobox.setItemText(0, _translate("MainWindow", "cisco_ios"))
        self.model_ssh_combobox.setItemText(1, _translate("MainWindow", "cisco_asa"))
        self.model_ssh_combobox.setItemText(2, _translate("MainWindow", "fortinet"))
        self.username_ssh.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Username: </span></p></body></html>"))
        self.password_ssh.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Password: </span></p></body></html>"))
        self.model_ssh.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Device Model: </span></p></body></html>"))
        self.purpose_ssh_combobox.setItemText(0, _translate("MainWindow", "Basic Troubleshooting"))
        self.purpose_ssh.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Purpose: </span></p></body></html>"))
        self.go_ssh_button.setText(_translate("MainWindow", "GO"))
        self.single_device_toolbox.setItemText(self.single_device_toolbox.indexOf(self.via_ssh_page), _translate("MainWindow", "via SSH"))
        self.purpose_console.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Purpose: </span></p></body></html>"))
        self.baud_rate.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Baud Rate: </span></p></body></html>"))
        self.com_port.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">COM Port: </span></p></body></html>"))
        self.model_console_combobox.setItemText(0, _translate("MainWindow", "cisco_ios"))
        self.model_console_combobox.setItemText(1, _translate("MainWindow", "cisco_asa"))
        self.model_console_combobox.setItemText(2, _translate("MainWindow", "fortinet"))
        self.go_console_button.setText(_translate("MainWindow", "GO"))
        self.purpose_console_combobox.setItemText(0, _translate("MainWindow", "Basic Troubleshooting"))
        self.model_console.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Device Model: </span></p></body></html>"))
        self.username_console.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Username: </span></p></body></html>"))
        self.password_console.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Password: </span></p></body></html>"))
        self.enable_console.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">Enable Secret: </span></p></body></html>"))
        self.single_device_toolbox.setItemText(self.single_device_toolbox.indexOf(self.via_console_page), _translate("MainWindow", "via CONSOLE"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.single_device_tab), _translate("MainWindow", "Single Device"))
        item = self.manual_device_table.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.manual_device_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "IP"))
        item = self.manual_device_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Username"))
        item = self.manual_device_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Password"))
        item = self.manual_device_table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Device Model"))
        item = self.manual_device_table.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Purpose"))
        self.add_row_button.setText(_translate("MainWindow", "+"))
        self.delete_row_button.setText(_translate("MainWindow", "-"))
        self.go_manual_button.setText(_translate("MainWindow", "GO"))
        self.multiple_device_toolbox.setItemText(self.multiple_device_toolbox.indexOf(self.manual_add_page), _translate("MainWindow", "Add Devices Manually"))
        self.go_file_button.setText(_translate("MainWindow", "GO"))
        self.get_file_button.setText(_translate("MainWindow", "Select a File"))
        self.multiple_device_toolbox.setItemText(self.multiple_device_toolbox.indexOf(self.file_add_page), _translate("MainWindow", "Import Devices from a File"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.multiple_device_tab), _translate("MainWindow", "Multiple Devices"))

        self.refillUi(MainWindow)

    # Fill up Qt Designer Code to fit our requirement
    def refillUi(self, MainWindow):
        ## Change Options (Device Model and Purpose)
        self.model_ssh_combobox.clear()
        self.model_ssh_combobox.addItems(self.models)
        self.purpose_ssh_combobox.clear()
        self.purpose_ssh_combobox.addItems(self.purpose)
        self.model_console_combobox.clear()
        self.model_console_combobox.addItems(self.models)
        self.purpose_console_combobox.clear()
        self.purpose_console_combobox.addItems(self.purpose)

        ## Embelishments
        # Single Device / via SSH
        self.device_ip_entry.setPlaceholderText("Enter IP...")
        self.device_ip_entry.setValidator(self.ipValidator)
        self.username_ssh_entry.setPlaceholderText("Enter Username...")
        self.password_ssh_entry.setPlaceholderText("Enter Password...")
        self.password_ssh_entry.setEchoMode(self.password_ssh_entry.Password)
        self.go_ssh_button.clicked.connect(self.go_ssh_button_clicked)

        # Single Device / via CONSOLE
        self.baud_rate_console_entry.setPlaceholderText("Baud Rate...")
        self.com_port_console_entry.setPlaceholderText("COM Port...")
        self.username_console_entry.setPlaceholderText("Enter Username...")
        self.password_console_entry.setPlaceholderText("Enter Password...")
        self.password_console_entry.setEchoMode(self.password_console_entry.Password)
        self.enable_console_entry.setPlaceholderText("Enter Enable Secret...")
        self.enable_console_entry.setEchoMode(self.enable_console_entry.Password)
        self.go_console_button.clicked.connect(self.go_console_button_clicked)

        # Multiple Devices / Add Devices Manually
        manual_device_current = self.manual_device_table.rowCount()
        for index in range(manual_device_current):
            #cell_mask = QtWidgets.QLineEdit.setEchoMode(Password)
            #self.manual_device_table.setCellWidget(index, 2, cell_mask)
            model_combo = QtWidgets.QComboBox()
            for t in self.models:
                model_combo.addItem(t)
            model_combo.setCurrentIndex(0)
            self.manual_device_table.setCellWidget(index, 3, model_combo)
            purpose_combo = QtWidgets.QComboBox()
            for t in self.purpose:
                purpose_combo.addItem(t)
            purpose_combo.setCurrentIndex(0)
            self.manual_device_table.setCellWidget(index, 4, purpose_combo)
            self.manual_device_table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.add_row_button.clicked.connect(self.add_row_button_clicked)
        self.delete_row_button.clicked.connect(self.delete_row_button_clicked)
        self.go_manual_button.clicked.connect(self.go_manual_button_clicked)

        # Multiple Devices / Import Devices from a File
        self.go_file_button.clicked.connect(self.go_file_button_clicked)
        self.get_file_button.clicked.connect(self.get_file_button_clicked)

if __name__ == "__main__":
    import sys
    logging.info('App Started.')
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())