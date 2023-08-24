## Install "pyserial" for serial communication, package "serial" won't work

import PySimpleGUIQt as sg
import time
import psutil
import re
import serial
import serial.tools.list_ports as stlp
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume


## Hide program window at startup
hide_on_startup = False
## List of processes names which volume you want to control
program_name_list = [[], [], [], [], []]
## Default serial port
default_com = ""
## List of systems serial ports
available_serial_ports = ["None"]
connection_status = False


## System tray logo
logo1 = b"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"

## GUI layout
layout = [
    [sg.Text("Connection status: Not connected", key = "connection_status")],
    [sg.Text("If connection does not work try changing COM port and hit 'Connect'")],
    [sg.InputCombo(available_serial_ports,
                    default_value = default_com,
                    size = (8, 1),
                    key = "com_combo",
                    readonly = True),
    sg.Button("Refresh", size = (8, 1), tooltip = "Refresh list of serial connections", button_color=("white", "black")),
    sg.Button("Connect", size = (8, 1), key = "connect", tooltip = "Connect / disconnect serial", button_color=("white", "black")),
    sg.Button("List audioprocesses", size = (15, 1), button_color=("white", "black"))],
    [sg.Output(size=(500, 200))]
    ]

## System tray menu layout
menu1 = ["&File", ["&Open", "&Minimize", "E&xit"]]

## Print blyaat
def blyat():
    print("blyaat")
    return

## Read settings from file
def read_settings():
    global default_com
    try:
        with open("AAM_settings.txt", "r") as f:
            while True:
                line = f.readline()
                ## End of the file
                if line == "":
                    break
                line = line.rstrip("\n")
                ## Skip comment lines
                if line.startswith("#"):
                    pass
                elif line.startswith("default_com"):
                    pos1 = line.find("=")
                    default_com = line[pos1+1:len(line)].rstrip("\n").strip()
                elif line.startswith("program"):
                    ## Program number
                    index = int(line[7])
                    ## Save part of the line which contains program name(s) into a list
                    program_names = line[11:len(line)].split(",")
                    ## Add programs from file to program_name_list
                    for program in program_names:
                        program_name_list[index - 1].append(program.strip())

    except IOError:
        print("Cannot read settings file. I/O Error!")


## Establish serial connection
def connect_serial(serial_port):
    if serial_port == "":
        print("No port to connect to!")
        return
    print("Connecting to a serial: '{}' ...".format(str(serial_port)))
    ## Open serial communication
    try:
        arduino_serial = serial.Serial(serial_port, 9600, timeout = 0.2)
        print("Serial connection '{}' activated!".format(serial_port))
        return arduino_serial
    except Exception as e:
        print(e)
        print("Connection to serial '{}' failed!".format(serial_port))
        return False

def read_serial(serial_port):
    ## Get string from serial and split it into values
    try:
        serial_data = str(serial_port.readline().decode("utf-8").rstrip("\n"))
        volume_data = serial_data.split(";")
        ## If we have all 6 sliders datas
        if(len(volume_data) == 5):
            ## Convert slider data to decimal
            for i in range(5):
                volume_data[i] = round(float(volume_data[i])/100, 2)
            return volume_data
        else:
            return []
    except:
        return

## Get available serial ports
def get_serial_ports():
    ## Get systems active serial ports
    serial_connections = stlp.comports()
    ## Clear list for serial connections
    available_serial_ports = []
    if len(serial_connections) != 0:
        ## Add serial devices to list
        for serial in serial_connections:
            available_serial_ports.append(serial.device)
    ## Update GUIs drop-down mwnu
    window.FindElement("com_combo").Update(values = available_serial_ports)
    ## Set choise in drop menu to default serial if available
    if default_com in available_serial_ports:
        window.FindElement("com_combo").Update(value = default_com)
    #return available_serial_ports
    return available_serial_ports

## Update connection status at the window
def update_connection_status(new_status):
    window.FindElement("connection_status").Update(value = "Connection status: {}".format(new_status))

## Get a list of audioprocesses of programs defined at "program_name_list"
def get_audioprocesses():
    ## All systems audioprocesses
    audioprocesses = AudioUtilities.GetAllSessions()
    ## List for wanted processes
    wanted_audioprocesses = []
    for audioprocess in audioprocesses:
        try:
            for programs in program_name_list:
                if audioprocess.Process.name().lower() in programs:
                    wanted_audioprocesses.append(audioprocess)
        except:
            pass
    ## Return a list of audioprosesses of defined applications
    #print(wanted_audioprocesses)
    return wanted_audioprocesses

## Get a list of all systems audioprocesses names
def get_audioprocesses_names():
    ## All systems audioprocesses
    audioprocesses = AudioUtilities.GetAllSessions()
    ## List for wanted processnames
    wanted_audioprocesses = []
    for audioprocess in audioprocesses:
        try:
            wanted_audioprocesses.append(audioprocess.Process.name())
        except:
            pass
    ## Return a list of audioprosesses
    # print(wanted_audioprocesses)
    return wanted_audioprocesses

## Set Volume mixer sliders according to sliders
def set_volumelevels(audioprocesses, volume_data):
    ## Listed programs to control
    for programs in program_name_list:
        for program in programs:
            for audioprocess in audioprocesses:
                try:
                    ## Lets find a correct audioprocess(ses) for listed program
                    if audioprocess.Process.name().lower() == program.lower():
                        ## Index for volume data
                        index = program_name_list.index(programs)
                        ## Audio processes volume
                        process_volume = audioprocess.SimpleAudioVolume
                        ## Volume in decimal number 0 - 1, according to systems master volume
                        current_volume = round(float(process_volume.GetMasterVolume()), 2)
                        #print(audioprocess.Process, current_volume)

                        # Set volume according to sliders position
                        if volume_data[index] == 0:
                            process_volume.SetMasterVolume(0, None)
                        elif current_volume != volume_data[index]:
                            process_volume.SetMasterVolume(volume_data[index], None)
                except:
                    pass

## GUI
window = sg.Window("ArduinoAudioMixer 0.8", icon = "AAM_icon_2.ico").Layout(layout)
window.Read(timeout = 0)
## Hide window on startup
if hide_on_startup:
    window.Hide()

## Sys tray
#tray = sg.SystemTray(menu=menu1, data_base64=logo1, tooltip = "ArduinoAudioMixer")
tray = sg.SystemTray(menu=menu1, filename = r"AAM_icon_1.ico", tooltip = "ArduinoAudioMixer")

## Read settings file
read_settings()
## Get available serial ports
available_serial_ports = get_serial_ports()
## If default com is available
if default_com in available_serial_ports:
    serial_port = default_com
    ## Connect to serial
    arduino_serial = connect_serial(serial_port)
else:
    ## No serial connection
    arduino_serial = False
    print("Cannot connect to a default serial port.\nPlease choose port and connect manually.")


while True:
    ## Read GUI
    (window_event, value) = window.Read(timeout = 0)
    ## Read systen tray
    tray_event = tray.Read(timeout = 0)

    ## Handle GUI events
    if window_event == "Refresh":
        print("Refreshing serial connection list...")
        available_serial_ports = get_serial_ports()
        print("Done")
    elif window_event == "connect":
        if arduino_serial == False:
            arduino_serial = connect_serial(value["com_combo"])
        else:
            try:
                arduino_serial.close()
                arduino_serial = False
            except:
                print("No port to connect to!")
    elif window_event == "Minimize":
        window.Hide()
    elif window_event == "List audioprocesses":
        audio_processes = get_audioprocesses_names()
        print("List of running audioprocesses:")
        for audioprocess_name in audio_processes:
            print(audioprocess_name)

    ## Handle tray events
    if tray_event == "Open" or tray_event == "__ACTIVATED__":
        window.UnHide()
    elif tray_event == "Minimize":
        window.Hide()
    elif tray_event == "Exit":
        break
    # if tray_event != "__TIMEOUT__":
    #     print(tray_event)

    ## If serial connection is active
    if arduino_serial:
        ## Read serial data
        volume_data = read_serial(arduino_serial)
        # print(volume_data)
        if volume_data:
            ## Get audioprosesses to control
            audio_processes = get_audioprocesses()
            ## Set audioprocesses volume levels
            set_volumelevels(audio_processes, volume_data)
        ## Update connection status if needed
        if connection_status != True:
            connection_status = True
            update_connection_status("Connected")
            window.FindElement("connect").Update("Disconnect")
    else:
        ## Update connection status when disconnect
        if connection_status != False:
            connection_status = False
            update_connection_status("Not connected")
            window.FindElement("connect").Update("Connect")
            print("Serial disconnected!")
