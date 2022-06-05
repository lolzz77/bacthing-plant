
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

class MyMqtt:
    def __init__(self, client, topic_list, grade_key, grade_val, grade_dict):
        self.client = client
        self.topic_list = topic_list
        self.grade_key = grade_key
        self.grade_val = grade_val
        self.grade_dict = grade_dict

    # Subcribe to topic (e.g: Cement, Water, etc)
    def subscribe(self, client: mqtt_client, topic_list, grade_val):
        # On_message = the func will only be triggered once server side sends msg
        #
        # You can find out what class type are those parameters
        # On debug window, expand the 'special variable' -> '__class__'
        def on_message(client, userdata, msg):
            topic = msg.topic[:-6]
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            if(msg.payload.decode()=="start"):
                return
            self.checkStop(msg.payload.decode(), topic)
            # self.publish(client, topic_list['topic'], "stop")
            # if(msg.payload.decode().isdigit()):
            #     amount = float(msg.payload.decode())
            # else:
            #     amount = -1
            # if (amount >= self.grade_val or amount == -1):
            #     self.publish(client, topic, "stop")
            # _20mm = grade['20mm']
            # _10mm = grade['10mm']
            # sand = grade['sand']
            # d100 = grade['d100']
            # d45 = grade['d45']

        self.client.subscribe(topic_list['relay'])
        self.client.subscribe(topic_list['weight'])

        # Notice that it passes function without paranthesis
        # You don tneed to pass arguments, it will receive argument from server automatically
        # https://www.geeksforgeeks.org/python-invoking-functions-with-and-without-parentheses/
        self.client.on_message = on_message

    # To stop node red cement weight
    # send 'stop' to the relay that is connected to loop
    # sending 'stop' to cement_relay that is connected to cement switch 
    # will only turn the switch off and the weight will still increasing
    # publish = send msg to the server
    #
    # Double click switch in Node Red
    # See On Payload and Off Payload
    # That's the message you should send to control the switch
    def publish(self, client, topic, msg):
        msg = msg
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            print(f"Sent `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    # Why i make this function
    # aparrently, the on_message function is independant from obj's attribute itself.
    # if you use self.grade_val here, the value is referred to the last row of grade_dict
    # e.g: cement should be 350, but it reffered to d45 one, that is 1400
    def checkStop(self, msg, topic):
        grade_val = self.grade_dict[topic]
        if(msg.isdigit()):
            amount = float(msg)
        else:
            amount = -1
        if(amount >= grade_val or amount == -1):
            self.publish(self.client, topic, "stop")
            self.on_message = None

def getKeys(dict):
    return dict.keys()

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

    obj_list = []
    grade_keys = getKeys(grade_dict)

    for key in grade_dict:
        topic_list = {
            'topic' : key,
            'relay' : key + '_relay',
            'weight' : key + 'weight'
        }
        grade_dict[key] *= inp_meter
        grade_val = grade_dict[key]
        # Every obj has correct of its own topic_list
        obj_list.append(MyMqtt(client, topic_list, key, grade_val, grade_dict))
    print(grade_dict)
    
    topic_list = []
    key = ""
    grade_val = 0
    grade_keys = []
    grade_dict = []

    for obj in obj_list:
        # have to put 'obj.topic_list' instead of 'topic_list'
        # if not, it will use the last elm of topic_list
        obj.subscribe(client, obj.topic_list, obj.grade_val)
        obj.publish(client, obj.topic_list['topic'], "start")

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
