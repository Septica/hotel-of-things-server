import sys
import json
import serial
import time
from threading import Thread
from bluetooth import *
from Kafka import KafkaConsumer

global arduino


def observer(queue, client_socket):
    while True:
        if mac_address is None: continue
        arduino_input = arduino.readline().decode().rstrip()
        if(arduino_input == "D"):
            print("scanning")
            devices = discover_devices(lookup_names = True)
            print("done")
            for addr, name in devices:
                print(addr,name)
                if(addr == mac_address):
                    queue.append(arduino_input)
                    client_socket.connect((mac_address, 1))
                    
def bluetooth_observer(queue):
    while True:
        data = client_socket.recv(1024)
        print(data)
        try:
            msg = data.decode()
            if(msg == "light_sleep"):
                queue.append("F")
            elif(msg == "deep_sleep"):
                queue.append("L")
            elif(msg == "awake"):
                queue.append("T")
                queue.append("H")
        except:
            pass

def user_input(queue):
    while True:
        arduino_input = input()
        queue.append(arduino_input)

def queue_consume(queue):
    while True:
        if(len(queue) > 0):
            arduino_input = queue.pop(0)
            if(arduino_input == "D"):
                print("DOOR UNLOCK")
                arduino.write("U".encode())
            elif(arduino_input == "H"):
                print("AC Higher")
                arduino.write("H".encode())
            elif(arduino_input == "L"):
                print("AC LOWER")
                arduino.write("L".encode())
            elif(arduino_input == "F"):
                print("Lamp Off")
                arduino.write("F".encode())
            elif(arduino_input == "T"):
                print("Lamp ON")
                arduino.write("T".encode())

if (len(sys.argv) != 1):
    sys.exit(2)

consumer = KafkaConsumer(value_deserializer=lambda v: json.loads(v.decode('utf-8')), key_deserializer=str.encode)
consumer.subscribe(sys.argv[1])
client_socket=BluetoothSocket( RFCOMM )
arduino = serial.Serial('/dev/ttyACM0',9600)
time.sleep(2) 
queue = []

thread_read = Thread(target=observer, args=(queue,client_socket,))
thread_input_read = Thread(target=user_input, args=(queue,))
thread_bluetooth_read = Thread(target=bluetooth_observer, args=(queue,))
thread_queue_consume = Thread(target=queue_consume, args=(queue,))
thread_read.start()
thread_input_read.start()
thread_bluetooth_read.start()
thread_queue_consume.start()

for message in consumer:
    if message["type"] == "CONNECT":
        mac_address = message["mac_address"]
    elif message["type"] == "DISCONNECT":
        mac_address = None