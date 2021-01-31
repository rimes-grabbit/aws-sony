from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import tvmethodprocessor
import time
import json
import os, sys


clientId="mypythoncodebutton"
IOTName="HomeRaspberry"

certificateFolder = "certificates"

AWSEndpoint = "YOUR-AWS_ENDPOINT"
AWSPort = YOUR_AWS_PORT 

AmazonCA = "AmazonCA.pem"
PrivateKey = "Rasp-private.key"
PirvateCert = "Rasp-cert.crt"

def get_path(filename):
    dirname, dummyfilename = os.path.split(os.path.abspath(sys.argv[0]))
    return os.path.join(dirname, "%s/%s" % (certificateFolder, filename))

class ShadowCallbackContainer:
  def __init__(self, deviceShadowInstance):
      self.deviceShadowInstance = deviceShadowInstance
      self.method_processor = tvmethodprocessor.TVMethodProcessor ()
  
  # Custom Shadow callback
  def customShadowCallback_Delta(self, payload, responseStatus, token):
      payloadDict = json.loads(payload)
      action = payloadDict["state"]["method"]
      params = payloadDict["state"]["params"]
      
      self.method_processor.execute_action(action, params)


def start_listening():
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
    myAWSIoTMQTTShadowClient.configureEndpoint(AWSEndpoint, AWSPort)
    myAWSIoTMQTTShadowClient.configureCredentials(get_path("AmazonCA.pem"), get_path("Rasp-private.key"), get_path("Rasp-cert.crt"))

    myAWSIoTMQTTShadowClient.connect()

    deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(IOTName, True)

    shadowCallbackContainer_Bot = ShadowCallbackContainer(deviceShadowHandler)
 
    # Listen on deltas
    deviceShadowHandler.shadowRegisterDeltaCallback(shadowCallbackContainer_Bot.customShadowCallback_Delta)
 

    # Loop forever
    while True: 
        time.sleep(0.2) 