
import serial.tools.list_ports

def getComList():
    return serial.tools.list_ports.comports()

