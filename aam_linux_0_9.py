## Install "pyserial" for serial communication, package "serial" won't work

import sys
import pulsectl
import serial
import serial.tools.list_ports as stlp

######################################## Global shit ########################################

## List of processes names which volume you want to control
program_name_list = [[],[], [], [], []]
## Default serial port
serial_port = ""
## Path to settings file
settingsfile = '/home/henzzzzi/Scripts/AAM_settings.txt'

title = '########## - ArduinoAudioMixer Linux 0.9 - Henzzzzi @ 2k20 - ##########'

######################################## Functions ########################################

## Command line arguments
def check_sys_arguments():
    ##print(title)
    if len(sys.argv) == 1:
        return
    elif sys.argv[1].strip('-') == 'listp':
        pulse = pulsectl.Pulse()
        print('Running audioprocesses:')
        #print(get_audioprocesses_names(get_audioprocesses(pulse)) + 'asd')

        audioprocesses, audioprocess_names = get_audioprocesses(pulse)

        for name in audioprocess_names:
            print(name)

        pulse.close()
        exit(0)
    elif sys.argv[1].strip('-') == 'listc':
        serial_ports = get_serial_ports()
        print('Currently available com ports:')
        for port in serial_ports:
            print(port)
        exit(0)
    elif sys.argv[1].strip('-') == 'help':
        print('Available arguments, use only one at the time:')
        print('-listp - Lists available audioprocesses')
        print('-listc - Lists available com ports')
        exit(0)
    else:
        print("Unknown argument '" + sys.argv[1].strip('-') + "'")
        exit(0)

def printMenu():
    print(title)
    print("1) List running audioprocesses")
    print("2) Show controlled programs")
    print("3) Add a program to controlled programs")
    print("4) Print available serial ports")


## Read settings from file
def read_settings(filename):
    global serial_port
    try:
        ## Try open file specified in command line argument
        with open(filename, "r") as f:
            while True:
                line = f.readline()
                ## End of the file
                if line == "":
                    break
                line = line.rstrip("\n")
                ## Skip comment lines
                if line.startswith("#"):
                    pass
                elif line.startswith("serial_port"):
                    pos1 = line.find("=")
                    serial_port = line[pos1+1:len(line)].rstrip("\n").strip()
                elif line.startswith("program"):
                    ## Program number
                    index = int(line[7])
                    ## Save part of the line which contains program name(s) into a list
                    program_names = line[11:len(line)].split(",")
                    ## Add programs from file to program_name_list
                    for program in program_names:
                        program_name_list[index - 1].append(program.strip())
    except Exception as e:
        print("Cannot read settings file. I/O Error!" + e)

## Get available serial ports
def get_serial_ports():
    ## List for available serial connections
    available_serial_ports = []
    ## Get systems active serial ports
    serial_connections = stlp.comports()
    if len(serial_connections) != 0:
        ## Add serial devices to list
        for serial in serial_connections:
            available_serial_ports.append(serial.device)
    #return available_serial_ports
    return available_serial_ports

## Establish serial connection
def connect_serial(serial_port):
    if serial_port == "":
        print("No port to connect to!")
        return
    print("Connecting to a serial: '{}' ...".format(str(serial_port)))
    ## Open serial communication
    try:
        arduino_serial = serial.Serial(serial_port, 9600, timeout = 1)
        print("Serial connection '{}' activated!".format(serial_port))
        return arduino_serial
    except Exception as e:
        print("Connection to serial '{}' failed because of exception: '{}'".format(serial_port, e))
        return False

## Get data from serial
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
    except KeyboardInterrupt as e:
        raise
    except:
        return

## Retrieves audioprocesses
def get_audioprocesses(pulse):
    try:
        all_prosesses = pulse.sink_input_list()
        return all_prosesses, get_audioprocesses_names(all_prosesses)
    except Exception as e:
        print('Failed to get audioprocesses, {}'.format(e))
        exit(0)

## Gets audioprocesses names from objects
def get_audioprocesses_names(all_prosesses):
    process_names = []
    #print(all_prosesses)
    try:
        for process in all_prosesses:
            #print(process)
            #print(str(process.proplist) + "\n") ## Print all info of process
            #print(process.AudioStream)
            #print(process.proplist.get('application.name'))
            #print(process.proplist.get('application.process.binary'))
            #process_name = process.proplist.get('name')
            #print(process[len(process)-1])
            #process_names.append(process.name)
            process_names.append(process.proplist.get('application.process.binary'))

        #print(process_names)
        #print(process_names)
        return process_names
    except Exception as e:
        print('Failed to get audioprocess names, {}'.format(e))
        pass
        #exit(0)

## Add prosesses, current and new volume levels and mute states to a list
def parse_volumedata(audioprocesses, volume_data, current_processes_names):
    try:
        ## Go through program names in defined list
        ## Double loop bcs there could be multiple programs for one slider

        ## List for prosesses
        process_volume_data = []
        ## Index of slider in volume data list
        slider_index = 0

        for program_names in program_name_list:
            #print(program_names)
            for program_name in program_names:
                #print(program_name)
                ## Go through program names of currently running prosesses
                ## Index has to be calculated this way - otherwise it breaks when one program has multiple instances
                process_index = 0
                ## Pair processes name with audioprocess and volume information
                for process_name in current_processes_names:
                    #print(process_name)
                    if program_name.lower() == process_name.lower():
                        ## Current volume as float with 2 decimals
                        current_volume = round(audioprocesses[process_index].volume.value_flat, 2)
                        ## Add prosess info to list
                        process_volume_data.append([process_name.lower(), current_volume, audioprocesses[process_index], volume_data[slider_index], False])
                    process_index = process_index + 1
            slider_index = slider_index + 1

        ## Check for mutes
        index = 0
        for process in process_volume_data:
            #print('mute:{}'.format(process[2].mute))
            muted = False
            index_2 = 0;
            for other_process in process_volume_data:
                ## Skip current process
                if index_2 != index:
                    ## If prosesses has same name
                    if process[0] == other_process[0]:
                        ## If vol equals 0 and other process with same name has vol not equal to 0
                        ## Or if program is muted from pulseAudio
                        if process[1] == 0 and other_process[1] != 0 or process[2].mute == 1:
                            process[4] = True   ## Muted
                            break
                index_2 += 1
            index += 1
        #print(process_volume_data)
        return process_volume_data

    except Exception as e:
        print('Failed parsing channel datas ,{}'.format(e))
        exit(0)

## Set volumelevels
def set_volumelevels(pulse, process_volume_data):
    ## process_volume_data[0], process name
    ## process_volume_data[1] current volume_data
    ## process_volume_data[2], pulse process -obj
    ## process_volume_data[3], slider volume
    ## process_volume_data[4], mute state, default false

    #print(process_volume_data)
    ## Set volumes
    for process in process_volume_data:
        ## If prosess is not muted, change volume
        if not process[4]:
            pulse.volume_set_all_chans(process[2], process[3])

    # except:
    #     print('Failed to set volumelevels')
    #     exit(0)


######################################## Actuaalinen program ########################################

def main():
    try:
        ######################################## Startup ########################################
        check_sys_arguments()
        ## Read settings from file specified in command line arguments
        read_settings(settingsfile)
        #print('{};{};'.format(serial_port, program_name_list))

        arduino_serial = None

        ## Get available serial ports
        available_serial_ports = get_serial_ports()
        ## Try to connect to serial if port specified in settings file is present
        if serial_port in available_serial_ports:
            arduino_serial = connect_serial(serial_port)
            ## If serial = False = connection failed
            if not arduino_serial:
                print('Serial unavailable')
                exit(0)
        else:
            print("Cannot connect to serial port '{}'. Port not found!".format(serial_port))
            exit(0)

        ## Create pulse -object
        pulse = pulsectl.Pulse()

        ## Empty variable
        audioprocesses = None
        volume_data = [0, 0, 0, 0, 0]
        old_volume_data = None

        ## At start request sliderdata
        arduino_serial.write("asdf;".encode())


        ######################################## Actuaalinen LOOP ########################################
        while True:


            if volume_data:
                old_volume_data = volume_data
            ## Read serial data
            if arduino_serial:
                volume_data = read_serial(arduino_serial)
                #print(volume_data)

                ## Get audioprocesses
                old_audioprocesses = audioprocesses
                audioprocesses, audioprocess_names = get_audioprocesses(pulse)

                ## Set volume levels if there is vol data
                if volume_data or audioprocesses != old_audioprocesses:
                    #print(";{};{}".format(audioprocess_names, old_audioprocess_names))
                    if volume_data:
                        process_volume_data = parse_volumedata(audioprocesses, volume_data, audioprocess_names)
                    else:
                        process_volume_data = parse_volumedata(audioprocesses, old_volume_data, audioprocess_names)
                    set_volumelevels(pulse, process_volume_data)


    except KeyboardInterrupt:
        print("Keyboard interrupt. Exiting...")
        if arduino_serial:
            arduino_serial.close()
        pulse.close()
    except Exception as e:
        print('Fuq')
        print(e)

    finally:
        ## Close serial if present
        try:
            arduino_serial.close()
            pulse.close()
        except:
            pass

        sys.exit()


main()
