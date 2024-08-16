import sys
import glob
import serial


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            print(s.name)
            print(s.get_settings())
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == '__main__':
    print(serial_ports())
    
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()    

    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
    
    print('')    
    print('VIDEO DEVICES:')
    import win32com.client
    wmi = win32com.client.GetObject ("winmgmts:")
    for usb in wmi.InstancesOf ("Win32_USBHub"):
        print(usb.DeviceID)
    
    exit 
    
    print('')    
    print('AUDIO DEVICES:')    
    import pyaudio
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        #print("Index " + str(i) + " :")
        dev = p.get_device_info_by_index(i)
        print("Index " + str(i) + " :" + dev.get('name'))
        #print("------------------------------------------------------------")