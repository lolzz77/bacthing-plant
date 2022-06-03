
# library
import random
import time
from threading import Thread  
import curses
import threading

# If you encounter a yellow line error where it state you dont have the library
# Just try run, apparently u have the lirbary but it wasn't updated in VS code
# This line somehow disappear if you re-select python interpreter or restart pc etc
from paho.mqtt import client as mqtt_client

# External Files
import mqttVar

broker = mqttVar.broker
port = mqttVar.port
cementRelay = mqttVar.cementRelay
waterRelay = mqttVar.waterRelay
cementWeight = mqttVar.cementWeight
waterWeight = mqttVar.waterWeight
cementTopic = mqttVar.cementTopic
waterTopic = mqttVar.waterTopic
client_id = mqttVar.client_id
grade30NormalMix = mqttVar.grade30NormalMix
grade20NormalMix = mqttVar.grade20NormalMix
gradeCMotar = mqttVar.gradeCMotar
gradePrint = """1 - Grade 30
2 - Grade 20
3 - Grade CMotar"""

# Establish connection
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to {broker} MQTT.")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# Subcribe to topic (e.g: Cement, Water, etc)
def subscribeTopic(client: mqtt_client, topic, grade, key):
    # On_message = the func will only be triggered once server side sends msg
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")    
        amount = -1
        if(msg.payload.decode().isdigit()):
            amount = float(msg.payload.decode())
        if (amount >= grade[key] or amount != -1):
            publish(client, key)
        # _20mm = grade['20mm']
        # _10mm = grade['10mm']
        # sand = grade['sand']
        # d100 = grade['d100']
        # d45 = grade['d45']

    # Subscribe to relay so you can control relay
    client.subscribe(topic[0])

    # Subcribe to weight, so you can see how much weight issued
    client.subscribe(topic[1])

    client.on_message = on_message

# To stop node red cement weight
# send 'stop' to the relay that is connected to loop
# sending 'stop' to cement_relay that is connected to cement switch 
# will only turn the switch off and the weight will still increasing
# publish = send msg to the server
#
# Double click switch in Node Red
# See On Payload and Off Payload
# That's the message you should send to control the switch
def publish(client, topic):
    msg = "stop"
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def getList(dict):
    return dict.keys()

def createThread(grade_list, client, grade_dict):
    for x in grade_list:
        topic = [x + '_relay', x + 'weight']
        x = threading.Thread(target=subscribeTopic(client, topic ,grade_dict, x), name=x+'_t')
        x.start()

def run():
    client = connect_mqtt()
    grade_dict = None
    while grade_dict == None:
        print(gradePrint)
        inp_grade = input('Choose Grade:')
        match inp_grade:
            case '1':
                grade_dict = grade30NormalMix
                msg = 'Grade 30 Normal Mix'
            case '2':
                grade_dict = grade20NormalMix
                msg = 'Grade 20 Normal Mix'
            case '3':
                grade_dict = gradeCMotar
                msg = 'Grade C Motar'
            # 'case _:' is the 'default:' in C++
            case _:
                print('Invalid Input')
    print('Chosen grade: ' + msg)

    inp_meter = float(input('Enter Cubic Meter:'))
    for x in grade_dict:
        grade_dict[x] *= inp_meter
    print(grade_dict)

    grade_list = getList(grade_dict)
    createThread(grade_list, client, grade_dict)

    # Paho Python client provides three loops
    # loop_start()
    # loop_forever()
    # loop()
    client.loop_forever()

# key_pressed = False

# def detect_key_press():
#     global key_pressed
#     stdscr = curses.initscr()
#     key = stdscr.getch()
#     key_pressed = True

# thread = Thread(target = detect_key_press)
# thread.start()
# while not key_pressed:
    # run()

run()