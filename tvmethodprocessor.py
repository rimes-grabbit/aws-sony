from api import sony_api

class TVMethodProcessor:

    def __init__(self):
      self.sony_api= sony_api.SonyAPI ()
      self.method_dict = {}
      self.method_dict['volume'] = self.set_volume 
      self.method_dict['mute'] = self.set_mute 
      self.method_dict['playcontent'] = self.set_channel
      self.method_dict['power'] = self.set_power_status
      self.method_dict['quickaction'] = self.set_quickaction
      self.method_dict['application'] = self.set_application


    def execute_action(self, action, params):
        action_method = self.method_dict[action]
        action_method(params)

    def set_application(self, params):
        if params["appid"] is not None:
            self.sony_api.set_application(app_id = params["appid"]) 

    def set_quickaction(self, params):
        if params["action"] is not None:
            self.sony_api.set_quickaction(action = params["action"]) 

    def set_volume(self, params):
        if params["volume"] is not None:
            self.sony_api.set_volume(params["volume"])    

    def set_mute(self, params):
        if "mute" in params  and params["mute"] is not None:
            self.sony_api.set_mute(params["mute"])  

    def set_channel(self, params):
        if "channel" in params and params ["channel"] is not None:
            self.sony_api.set_channel(params["channel"])  
    
    def set_power_status(self, params):
        if "status" in params and params ["status"] is not None:
            self.sony_api.set_power_status(params["status"] == "on")          
        