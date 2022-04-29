import serial.tools.list_ports
import os
import time
import msvcrt
import sys
import signal

UART_BAUD_RATE = 115200
UART_TIMEOUT = 0.1
# UART_READ_BYTES = 30

INPUT_TIMEOUT = 0.1
   

g_uart_stop_read = False

########################################
#           COM Port detection
########################################
print("Connected COM ports: ")
# if msvcrt.kbhit():
    # if msvcrt.getch() == b"c":
        # os.system("cls")

comlist = serial.tools.list_ports.comports()
connected = []
for element in comlist:
    connected.append(element.device)
print(str(connected))

if len(connected) == 0:
    print("Please check com port...")
    sys.exit(0)

if len(connected) == 1:
    comport_name = connected[0]
    print(" => Auto set to " + comport_name + "\n")
else:
    while True:
            
        comport_num = input("Please set com port number: ")
        if ("COM" + comport_num) in connected:
            comport_name = "COM" + comport_num
            print("OK")
            break
        else:
            print("Please check com port number...")

########################################
#           Open COM Port
########################################
comport_sel = serial.Serial()
comport_sel.baudrate = UART_BAUD_RATE
comport_sel.port = comport_name
comport_sel.timeout = UART_TIMEOUT
comport_sel.open()
print(comport_sel)
   
########################################
#           Show UART message
########################################
while True:

    # One key function
    if msvcrt.kbhit():
        one_char = msvcrt.getch()
        if one_char == b"c":
            print("Clear screen")
            os.system("cls")
        elif one_char == b"s":
            g_uart_stop_read = not g_uart_stop_read
            if g_uart_stop_read:
                print("Stop reading uart message")
            else:
                print("Start to read uart message")
        elif one_char == b"p":
            if comport_sel.isOpen():
                comport_sel.close()
                print(comport_sel.port + " is closed")
            else:
                comport_sel.open()
                print(comport_sel.port + " is open")
        elif one_char == chr(27).encode():
            sys.exit(0)
    
    if not comport_sel.isOpen():
        time.sleep(1)
        continue
    
    #Check if stop reading uart message
    if g_uart_stop_read:
        comport_sel.flushInput()
        time.sleep(0.2)
        continue

    # Get console's columns for uart reading bytes
    columns, lines = os.get_terminal_size()
    read_msg_num = (columns - 3 - 1) // 4

    # Read uart message
    read_msg = comport_sel.read(read_msg_num)        # read_msg = comport_sel.read(UART_READ_BYTES)
    if len(read_msg) == 0:
        continue
    
    print_msg = " | "
    print_hex = ""  #"("
    for read_byte in read_msg:
        if read_byte < 0x20 or read_byte > 0x7F:
            print_msg += '.'
        else:
            print_msg += chr(read_byte)
        print_hex += hex(read_byte)[2:].zfill(2) + " "
    print_hex = print_hex.ljust(read_msg_num * 3 )
    print(print_hex + print_msg)

# os.system("pause")
