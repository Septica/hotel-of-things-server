import serial
import time
from threading import Thread

global arduino


def observer(queue):
    while True:
        arduino_input = arduino.readline().decode().rstrip()
        queue.append(arduino_input)

def user_input(queue):
    while True:
        arduino_input = input()
        queue.append(arduino_input)
arduino = serial.Serial('COM4',9600)
time.sleep(2) 
queue = []
thread_read = Thread(target=observer, args=(queue,))
thread_input_read = Thread(target=user_input, args=(queue,))
thread_read.start()
thread_input_read.start()
while True:
    if(len(queue) > 0):
        arduino_input = queue.pop(0)
        if(arduino_input == "D"):
            print("DOOR UNLOCK")
            arduino.write("U".encode())
            arduino_input == "0"
        elif(arduino_input == "H"):
            print("AC Higher")
            arduino.write("H".encode())
            arduino_input == "0"
        elif(arduino_input == "L"):
            print("AC LOWER")
            arduino.write("L".encode())
            arduino_input == "0"
        elif(arduino_input == "F"):
            print("Lamp Off")
            arduino.write("F".encode())
            arduino_input == "0"
    
