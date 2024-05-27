# Importing Libraries
import serial
import time

arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1)
arduino.reset_input_buffer()
arduino.reset_output_buffer()



def sendData():
    count = 1
    try:
        while True:
            dataToTransmit = "data:" + str(count)
            dataReceived = "a:b"
            count=count+1
            time.sleep(0.05)
            print(dataToTransmit)
            if (dataToTransmit != ""):
                arduino.write(bytes(dataToTransmit,'utf-8'))
                print("PC ->" +  dataToTransmit)
                
                
                          
    except KeyboardInterrupt:
        print("Serial Comm Closed")
        arduino.close()


if (__name__== "__main__"):
    sendData()