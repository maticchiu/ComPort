import serial.tools.list_ports
import os
import time
import msvcrt

print("Connected COM ports: ")
while True:
    if msvcrt.kbhit():
        if msvcrt.getch() == b"c":
            os.system("cls")
        else:
            break
    comlist = serial.tools.list_ports.comports()
    connected = []
    for element in comlist:
        connected.append(element.device)
    print(str(connected))
    #print("Connected COM ports: " + str(connected))
    time.sleep(1)

# os.system("pause")
