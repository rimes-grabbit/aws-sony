import requests
import json
import time

from api import irc_commands
from threading import Thread
from wakeonlan import send_magic_packet

IP = "192.168.1.104"
MAC = "3C:07:71:E4:41:C5"

HOST = "http://" + IP + "/"
API_IRC_COMMAND = "sony/IRCC"
API_AUDIO_COMMAND = "sony/audio"
API_APPLICATION_COMMAND = "sony/appControl"
API_PLAYINGCONTENT_COMMAND = "sony/avContent"
API_TOKEN = "sony/accessControl"
API_KEY = "07316064ebf6486d2a0288d1689d14589b153a33e86e40a8b39277c7c3afddee"

CONTENT_TYPES = {
            "xml":"application/xml",
            "json":"application/json"
        }

METHODS = {
     "volume": {"method":"setAudioVolume", "id":601},
     "mute" : {"method":"setAudioMute", "id":601},
     "channel" : {"method":"setPlayContent", "id":101},
     "application" : {"method":"setActiveApp", "id":601}

}

COOKIE_REQUEST = {
   "method":"actRegister",
   "params":[
      {
         "clientid":"RaspPython",
         "nickname":"RaspberryControl",
         "level":"private"
      },
      [
         {
            "value":"yes",
            "function":"WOL"
         }
      ]
   ],
   "id":1,
   "version":"1.0"
}

class SonyAPI:

    def __init__(self):
        self._host = HOST
        self._irc_commands = irc_commands.IRCCommands()  
        self.api_key = ""
           


    def refresh_api_key(self):
        response = self.send_json_request(API_TOKEN, COOKIE_REQUEST)

        header_values = dict(item.split("=") for item in response.headers['Set-cookie'].split("; ")) 

        self.api_key  = header_values["auth"] 
    
    def run_background_thread(self):

        while True:
            time.sleep(86400) # Sleep for 86400 second
            self.refresh_api_key()
            
    def get_channel_uri(self, channel_name):
        if channel_name in irc_commands.channels:
            return irc_commands.channels[channel_name]

        return None

    def get_header(self, request_type):
        '''
        header = dict(cookies=self._cookies)

        headers = []
        headers.append("Content-Type": CONTENT_TYPES[request_type])
        headers.append( "Cookie":"auth=" + API_KEY)
        return json.dumps(headers)'''
        
        return {
            "Content-Type": CONTENT_TYPES[request_type],
            "Cookie":"auth=" + self.api_key
          
        }
    def xml_action(self, actionCode):
        return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>"
               "<s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"" 
               " s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">"
               "<s:Body><u:X_SendIRCC xmlns:u=\"urn:schemas-sony-com:service:IRCC:1\">"
               "<IRCCCode>" + actionCode + "</IRCCCode></u:X_SendIRCC></s:Body></s:Envelope>")


    def json_action(self, method, params, version="1.0"):
        return {
            'method': METHODS[method]['method'],
            'id':  METHODS[method]['id'],
            "params": [params],
            "version": version
        }

    
    def do_post (self, url, data, headers, reauthenticated = False):
        response = requests.post(url, data = data,  headers = headers)
        if (response.status_code == 403) and (not reauthenticated):
            print(f"<<Try again ERROR Authentication, data: {data}  >>")
            self.refresh_api_key()
            self.do_post(url = url, data = data, headers = self.get_header(list(CONTENT_TYPES.keys())[list(CONTENT_TYPES.values()).index(headers["Content-Type"])]), reauthenticated = True)
            return
        
        print(f"<< Response: {response}, data: {data}  >>")
       
        return response
        
    def send_xml_request(self, action):
        xml_data = self.xml_action(self._irc_commands.commands[action])
        return self.do_post(url = self._host + API_IRC_COMMAND, data = xml_data, headers = self.get_header("xml"))
        

    def send_json_request(self, api, json_data, reauthenticated = False):
        headers = []
        headers.append(self.get_header("json"))
        return  self.do_post(url = self._host + api, data = json.dumps(json_data),  headers = self.get_header("json")) 

    def turn_on(self):
        send_magic_packet(MAC,
                   ip_address=IP,
                   port=1337)

    def set_power_status(self, status):
        if status == True:
            self.turn_on()
        else:
            self.send_xml_request("Power Off")

    def set_quickaction(self, action):
        self.send_xml_request(action = action)
        
    def set_mute (self, is_mute):
        params_str = '{"status": %s}' % str(is_mute).lower()
        params = json.loads(params_str)

        json_data = self.json_action(method = 'mute', params = params)

        self.send_json_request(api = API_AUDIO_COMMAND, json_data=json_data)

    def set_volume(self, volume):
        params = json.loads('{"volume": "%s", "target": "speaker"}' % (volume))

        json_data = self.json_action(method = 'volume', params = params)

        self.send_json_request(api = API_AUDIO_COMMAND, json_data=json_data)

    def set_application(self, app_id):
        params = json.loads('{"uri": "%s"}' % (irc_commands.applications[app_id]))

        json_data = self.json_action(method = 'application', params = params)

        self.send_json_request(api = API_APPLICATION_COMMAND, json_data=json_data)

    def set_channel(self, channel):
        channel_uri = self.get_channel_uri(channel)
        if channel_uri is not None:
            request_string = '{"uri": "%s"}' % (channel_uri)
            params = json.loads(request_string)
            json_data = self.json_action(method = 'channel', params = params)
            self.send_json_request(api = API_PLAYINGCONTENT_COMMAND, json_data=json_data)

        







    
