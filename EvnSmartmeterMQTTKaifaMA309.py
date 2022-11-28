from dotenv import load_dotenv
from gurux_dlms.GXByteBuffer import GXByteBuffer
import serial

from binascii import unhexlify
import os
import sys
import logging
import time

import paho.mqtt.client as mqtt
from gurux_dlms.GXDLMSTranslator import GXDLMSTranslator
from gurux_dlms.GXDLMSTranslatorMessage import GXDLMSTranslatorMessage
from bs4 import BeautifulSoup

load_dotenv()

# Config Parameter aus .env auslesen
PORT = os.getenv('PORT')
BAUD = os.getenv('BAUD')
# EVN Schlüssel zB. "36C66639E48A8CA4D6BC8B282A793BBB"
KEY = unhexlify(os.getenv('KEY'))
LOGLEVEL = os.getenv('LOGLEVEL')

MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')
MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_TOPIC = os.getenv('MQTT_TOPIC')

# MQTT Broker IP adresse Eingeben ohne Port!
mqttBroker = MQTT_HOST
mqttuser = MQTT_USER
mqttpasswort = MQTT_PASS

# Aktuelle Werte auf Console ausgeben (True | False)
printValue = False

logging.basicConfig(filename='./log/smartmeter.log', level=LOGLEVEL)
log = logging.getLogger('meter')

# MQTT Init
if MQTT_HOST:
    try:
        client = mqtt.Client("SmartMeter")
        client.username_pw_set(mqttuser, mqttpasswort)
        client.connect(mqttBroker, port=MQTT_PORT)
    except Exception as e:
        print("Die Ip Adresse des Brokers ist falsch!")
        print(e)
        sys.exit()

tr = GXDLMSTranslator()
tr.blockCipherKey = GXByteBuffer(KEY)
tr.comments = True
ser = serial.Serial(port=PORT,
                    baudrate=BAUD,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    )

while 1:
    daten = ser.read(size=282).hex()
    log.debug(daten)

    msg = GXDLMSTranslatorMessage()
    msg.message = GXByteBuffer(daten)
    xml = ""
    pdu = GXByteBuffer()
    tr.completePdu = True
    while tr.findNextFrame(msg, pdu):
        pdu.clear()
        xml += tr.messageToXml(msg)

    soup = BeautifulSoup(xml, 'lxml')

    results_32 = soup.find_all('uint32')
    results_16 = soup.find_all('uint16')

    # Wirkenergie A+ in KiloWattstunden
    WirkenergieP = int(str(results_32)[16:16 + 8], 16) / 1000

    # Wirkenergie A- in KiloWattstunden
    WirkenergieN = int(str(results_32)[52:52 + 8], 16) / 1000

    # Momentanleistung P+ in Watt
    MomentanleistungP = int(str(results_32)[88:88 + 8], 16)

    # Momentanleistung P- in Watt
    MomentanleistungN = int(str(results_32)[124:124 + 8], 16)

    # Spannung L1 in Volt
    SpannungL1 = int(str(results_16)[16:20], 16) / 10

    # Spannung L2 in Volt
    SpannungL2 = int(str(results_16)[48:52], 16) / 10

    # Spannung L3 in Volt
    SpannungL3 = int(str(results_16)[80:84], 16) / 10

    # Strom L1 in Ampere
    StromL1 = int(str(results_16)[112:116], 16) / 100

    # Strom L2 in Ampere
    StromL2 = int(str(results_16)[144:148], 16) / 100

    # Strom L3 in Ampere
    StromL3 = int(str(results_16)[176:180], 16) / 100

    # Leistungsfaktor
    Leistungsfaktor = int(str(results_16)[208:212], 16) / 1000

    payload = f'{{\
                        "kWh_in": {WirkenergieP}, \
                        "kWh_out": {WirkenergieN}, \
                        "pwr_in": {MomentanleistungP}, \
                        "pwr_out": {MomentanleistungN}, \
                        "pwr": {MomentanleistungP - MomentanleistungN}, \
                        "voltage_l1": {SpannungL1}, \
                        "voltage_l2": {SpannungL2}, \
                        "voltage_l3": {SpannungL3}, \
                        "current_l1": {StromL1}, \
                        "current_l2": {StromL2}, \
                        "current_l3": {StromL3}, \
                        "power_factor": {Leistungsfaktor} \
                }}'

    log.debug(payload)

    # MQTT
    if MQTT_HOST:
        connected = False
        while not connected:
            try:
                client.reconnect()
                connected = True
            except Exception as e:
                print(f"Lost Connection to MQTT...Trying to reconnect in 2 Seconds ({e})")
                time.sleep(2)

        client.publish(f"{MQTT_TOPIC}/WirkenergieP", WirkenergieP)
        client.publish(f"{MQTT_TOPIC}/WirkenergieN", WirkenergieN)
        client.publish(f"{MQTT_TOPIC}/MomentanleistungP", MomentanleistungP)
        client.publish(f"{MQTT_TOPIC}/MomentanleistungN", MomentanleistungN)
        client.publish(f"{MQTT_TOPIC}/Momentanleistung", MomentanleistungP - MomentanleistungN)
        client.publish(f"{MQTT_TOPIC}/SpannungL1", SpannungL1)
        client.publish(f"{MQTT_TOPIC}/SpannungL2", SpannungL2)
        client.publish(f"{MQTT_TOPIC}/SpannungL3", SpannungL3)
        client.publish(f"{MQTT_TOPIC}/StromL1", StromL1)
        client.publish(f"{MQTT_TOPIC}/StromL2", StromL2)
        client.publish(f"{MQTT_TOPIC}/StromL3", StromL3)
        client.publish(f"{MQTT_TOPIC}/Leistungsfaktor", Leistungsfaktor)

        client.publish(f"{MQTT_TOPIC}/values", payload)

    # except BaseException as err:
    #   print("Fehler beim Synchronisieren. Programm bitte ein weiteres mal Starten.")
    #   print()
    #   print("Fehler: ", format(err))

    #   sys.exit()
