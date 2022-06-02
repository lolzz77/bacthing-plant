import random

# interlink.dyndns.biz
# port 1880 - node red
# port 1883 - mqtt
broker = 'interlink.dyndns.biz'
port = 1883

cementRelay = 'cement_relay'
waterRelay = 'water_relay'

cementWeight = 'cementweight'
waterWeight = 'waterweight'

# Double click on switch
# see 'Topic'
# that's the name you have to follow
cementTopic = 'cement'
waterTopic = 'water'

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'

# Ingredient Grade
# G30
grade30NormalMix = {
        'cement': 350,
        'water': 180,
        '20mm': 930,
        '10mm': 360,
        'sand': 546,
        'total': 1836,
        'd100': 2100,
        'd45': 1400
    }

# 20
grade20NormalMix = {
        'cement': 300,
        'water': 180,
        '20mm': 930,
        '10mm': 360,
        'sand': 600,
        'd45': 1500,
        'total': 1890
    }

# GCMotar
gradeCMotar = {
    'cement': 300,
    'water': 200,
    'sand': 1540,
    'd45': 1500,
    'total': 1540
    }
