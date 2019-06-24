import RPi.GPIO as GPIO
import dht11
import time
import sys
import ibmiotf.application
import ibmiotf.device
import random

#Provide your IBM Watson Device Credentials
organization = "mtdslt"
deviceType = "Smartcargo"
deviceId = "123"
authMethod = "token"
authToken = "12345678"

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# read data using pin 12
SensorInstance = dht11.DHT11(pin = 16)


# Initialize the device client.
T=0
H=0

def myCommandCallback(cmd):
        print("Command received: %s" % cmd.data)
       
        
        if cmd.command == "setInterval":
                if 'interval' not in cmd.data:
                        print("Error - command is missing required information: 'interval'")
                else:
                        interval = cmd.data['interval']
        elif cmd.command == "print":
                if 'message' not in cmd.data:
                        print("Error - command is missing required information: 'message'")
                else:
                        print(cmd.data['message'])

try:
	deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
	deviceCli = ibmiotf.device.Client(deviceOptions)
	#..............................................
	
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()

# Connect and send a datapoint "hello" with value "world" into the cloud as an event of type "greeting" 10 times
deviceCli.connect()

while True:
        #Get Sensor Data from DHT11
        SensorData = SensorInstance.read()
        GPIO.setup(7,GPIO.IN)

        #GPIO.add_event_detect(7,GPIO.RISING)
        MQ = GPIO.input(7)
        if MQ==0:
                print ("not fire")
        else:
                print ("fire")
        if SensorData.is_valid():
        #if True:
            T = SensorData.temperature
            H = SensorData.humidity
        else:
            print "SensorData Invalid"
        #Send Temperature & Humidity to IBM Watson
        data = { 'Temperature' : T, 'Humidity': H ,'MQ': MQ}
        #print data
        def myOnPublishCallback():
            print "Published Temperature = %s C" % T, "Humidity = %s %%" % H,"MQ = %s %%" % MQ, "to IBM Watson"

        success = deviceCli.publishEvent("DHT11", "json", data, qos=0, on_publish=myOnPublishCallback)
        if not success:
            print("Not connected to IoTF")
        time.sleep(1)
        
        deviceCli.commandCallback = myCommandCallback

# Disconnect the device and application from the cloud
deviceCli.disconnect()
