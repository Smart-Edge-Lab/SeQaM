import os
import sys
from queue import Queue

from ModuleManagement.DataModels.event import ChangeBandwidthEvent, ConnectEvent, DisconnectEvent, MigrateEvent, \
    GenerateNetworkLoadEvent, NetworkEvent
from ModuleManagement.console import output_to_console

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from Modules.EventOrchestrator.NetworkEventsRequester import NetworkEventsRequester


class Requests:
    def __init__(self):
        pass


class NetworkRequests(Requests):
    def __init__(self) -> None:
        super().__init__()
        self._requester_ = NetworkEventsRequester()

    def generate_network_load(self, event: GenerateNetworkLoadEvent):
        print(
            f"NETWORK EVENT: Generate network load in route:{event.src_device_name}->{event.dst_device_name}, "
            f"interface  {event.interface} load-->{event.load} for {event.time}"
        )
        self._requester_.requestGenerateNetworkLoad(event)


class NetworkEventInterpreter():

    def __init__(self):
    
        self.net_event_queue= Queue[NetworkEvent](maxsize = 3)
        self.net_translator_engine = NetworkEventsTranslator()
        self.NETWORK_EVENT_ACTIONS = ["connect", "disconnect", "migrate", "network_load", "network_bandwidth"]
        # all commands related to network should be declared here
        # TODO: can get rid of NETWORK_EVENT_ACTIONS, but it is used for validation in the main module

    def interpret_event(self, event: NetworkEvent):
        """
        Interpret the event and return the corresponding command
        """
        try:
            if isinstance(event, ConnectEvent):
                self.net_translator_engine.connectDevice(event)
            elif isinstance(event, DisconnectEvent):
                self.net_translator_engine.disconnectDevice(event)
            elif isinstance(event, MigrateEvent):
                self.net_translator_engine.migrateDevice(event)
            elif isinstance(event, GenerateNetworkLoadEvent):
                self.net_translator_engine.generateNetworkLoad(event)
            elif isinstance(event, ChangeBandwidthEvent):
                self.net_translator_engine.changeBandwidth(event)
            else:
                # Handle the case when action is not found
                print (f"Unknown action: {event.action}")
                
        except Exception as e:
            output_to_console(self.__class__.__name__, e)

    def networkEventInterpreter_runner(self):
        """ 
        Run a thread to listen to the event queue. When an event arrives, interpret it and run the
        corresponding method.
        """
        while True:        
            event = self.net_event_queue.get()
            #print("forwarding event {}, to network".format(event))
            self.interpret_event(event)
            


class NetworkEventsTranslator():

    def __init__(self) -> None:

        self._devices_ = ["server", "ue", "router", "switch", "poa"]
        self._requester_: dict[str, Requests] = {}

        try :        
            for device in self._devices_:
                device_lower = device.lower()
                #TODO: This validation seems to be useless
                if device_lower in self._devices_:
                    requester_class: type[Requests] = {
                        "server": ServerNetworkRequests,
                        "ue": UserEquipmentNetworkRequests,
                        "router": RouterNetworkRequests,
                        "switch": SwitchNetworkRequests,
                        "poa": PoANetworkRequests,
                    }[device_lower]
                    self._requester_[device] = requester_class()
        except:
            print ("NETWORK EVENT: Device configuration file not found")


    def validateDevice(self,device_type) -> bool:
        """
        Validates if the type of the device exists. 

        Parameters:
        device_type (str): The type of the device.
        
        Returns:
        Bool
        """ 
        if device_type in list(self._requester_.keys()):
            return True   
        else:
            print (f"NETWORK EVENT: Device type is not accepted")
            return False   
        

    def connectDevice(self, event: ConnectEvent) -> None:
        """
        Connect a device. (Not implemented)

        Parameters:
        src_device_type (str): The type of the source device.
        src_device_name (str): The name of the source device.
        dst_device_type (str): The type of the destination device to which the source device should connect.
        dst_device_name (int): The name of the destination device to which the source device should connect.
        
        Returns:
        None
        """ 
        
        if self.validateDevice (event.src_device_type) and self.validateDevice (event.dst_device_type):
            requester = self.get_requester(event)
            if isinstance(requester, ServerNetworkRequests):
                requester.requestConnectServer(event)
            elif isinstance(requester, UserEquipmentNetworkRequests):
                requester.requestConnectUE(event)
            # Add more conditions for other device types if needed
        else:
            print(f"NETWORK EVENT: Invalid device type: {event.src_device_type} or {event.dst_device_type}")


    def disconnectDevice(self, event: DisconnectEvent) -> None:
        """
        Disconnect a device. (Not implemented)

        Parameters:
        src_device_type (str): The type of the source device.
        src_device_name (str): The name of the source device.
        dst_device_type (str): The type of the destination device from which the source device should disconnect.
        dst_device_name (int): The name of the destination device from which the source device should disconnect.
        
        Returns:
        None
        """ 

        if self.validateDevice (event.src_device_type) and self.validateDevice (event.dst_device_type):
            requester = self.get_requester(event)
            if isinstance(requester, ServerNetworkRequests):
                requester.requestDisconnectServer(event)
            elif isinstance(requester, UserEquipmentNetworkRequests):
                requester.requestDisconnectUE(event)
            # Add more conditions for other device types if needed
        else:
            print(f"NETWORK EVENT: Invalid device type: {event.src_device_type} or {event.dst_device_type}")


    def migrateDevice(self, event: MigrateEvent) -> None:
        """
        Migrate a device. (Not implemented)

        Parameters:
        src_device_type (str): The type of the source device.
        src_device_name (str): The name of the source device.
        dst_device_type (str): The type of the destination device.
        dst_device_name (int): The name of the destination device.
        
        Returns:
        None
        """ 
        if self.validateDevice (event.src_device_type) and self.validateDevice (event.dst_device_type):
            requester = self.get_requester(event)
            if isinstance(requester, ServerNetworkRequests):
                requester.requestMigrateServer(event)
            elif isinstance(requester, UserEquipmentNetworkRequests):
                requester.requestMigrateUE(event)
            # Add more conditions for other device types if needed
        else:
            print(f"NETWORK EVENT: Invalid device type: {event.src_device_type} or {event.dst_device_type}")


    def generateNetworkLoad(self, event: GenerateNetworkLoadEvent):
        """
        Generate network load for a given device.

        Parameters:
        src_device_type (str): The type of the source device.
        src_device_name (str): The name of the source device.
        interface (str): The interface of the source device.
        network_load (int): The amount of network load to generate.
        time (str): The time the network load should be generated, ending in s,m,h second/minute/hour
        
        Returns:
        None
        """
        if self.validateDevice (event.src_device_type):
            requester = self.get_requester(event)
            if isinstance(requester, RouterNetworkRequests):
                requester.generateNetworkLoadInRouter(event)
            elif isinstance(requester, PoANetworkRequests):
                requester.generateNetworkLoadInPoA(event.src_device_name)
            elif isinstance(requester, SwitchNetworkRequests):
                requester.generateNetworkLoadInSwitch(event.src_device_name)
            elif isinstance(requester, NetworkRequests):
                requester.generate_network_load(event)
            # Add more conditions for other device types if needed
        else:
            print(f"NETWORK EVENT:Invalid device type: {event.src_device_type}")

    def get_requester(self, event: NetworkEvent):
        return self._requester_[event.src_device_type] if event.src_device_type else None

    def changeBandwidth(self, event: ChangeBandwidthEvent):
        """
        Change the bandwidth of a device.

        This method changes the bandwidth of a device for a given time period.

        Parameters:
        src_device_type (str): The type of the source device.
        src_device_name (str): The name of the source device.
        interface (str): The interface of the source device.
        bandwidth (int): The new bandwidth to set.
        time (str): The time the bandwidth change should be applied, ending in s,m,h (second/minute/hour)
        
        Returns:
        None
        """ 
        if self.validateDevice (event.src_device_type):
            requester = self.get_requester(event)
            if isinstance(requester, RouterNetworkRequests):
                requester.changeBandwidthInRouter(event)
        else:
            print(f"NETWORK EVENT:Invalid device type: {event.src_device_type}")



class UserEquipmentNetworkRequests(NetworkRequests):

    def requestConnectUE(self, event: ConnectEvent) -> None:
        print(f"NETWORK EVENT: Connect ue:{event.src_device_name} to {event.dst_device_type}:{event.dst_device_name}")

    def requestDisconnectUE(self, event: DisconnectEvent) -> None:
        print(f"NETWORK EVENT: Disconnect ue:{event.src_device_name} from {event.dst_device_type}:{event.dst_device_name}")

    def requestMigrateUE(self, event: MigrateEvent) -> None:
        print(f"NETWORK EVENT: Migrate ue:{event.src_device_name} to {event.dst_device_type}:{event.dst_device_name}")


class ServerNetworkRequests(NetworkRequests):
    
    def __init__(self) -> None:
        super().__init__()


    def requestConnectServer(self, event: ConnectEvent) -> None:
        print(f"NETWORK EVENT: Connect server:{event.src_device_name} to {event.dst_device_type}:{event.dst_device_name}")


    def requestDisconnectServer(self, event: DisconnectEvent) -> None:
        print(f"NETWORK EVENT: Disconnect server:{event.src_device_name} from {event.dst_device_type}:{event.dst_device_name}")


    def requestMigrateServer(self, event: MigrateEvent) -> None:
        print(f"NETWORK EVENT: Migrate server:{event.src_device_name} to {event.dst_device_type}:{event.dst_device_name}")



class SwitchNetworkRequests(NetworkRequests):
    
    def __init__(self) -> None:
        super().__init__()


    def generateNetworkLoadInSwitch(self, src_device_name):
        print(f"NETWORK EVENT: Generate network load in switch:{src_device_name}")



class RouterNetworkRequests(NetworkRequests):

    def generateNetworkLoadInRouter(self, event: GenerateNetworkLoadEvent):
        print(f"NETWORK EVENT: Generate network load in route:{event.src_device_name}, interface  {event.interface} load-->{event.load} for {event.time}")
        self._requester_.requestGenerateNetworkLoad(event)

    def changeBandwidthInRouter(self, event: ChangeBandwidthEvent):
        print(f"NETWORK EVENT: Change badwidth in router:{event.src_device_name}, interface  {event.interface} to-->{event.bandwidth} for {event.time}")
        self._requester_.requestChangeBandwidth(event)



class PoANetworkRequests(NetworkRequests):
    
    def __init__(self) -> None:
        super().__init__()

    def generateNetworkLoadInPoA(self, src_device_name):
        print(f"NETWORK EVENT: Generate network load in poa:{src_device_name}")





if __name__ == "__main__":
    engine = NetworkEventsTranslator()
    engine.connectDevice(ConnectEvent(action="connect", src_device_type = "ue", src_device_name = "ue1", dst_device_type = "poa", dst_device_name = "poa1", time='10s', interface='eth0'))
    engine.disconnectDevice(DisconnectEvent(action="disconnect", src_device_type = "ue", src_device_name = "ue5", dst_device_type = "server", dst_device_name = "svr1", time='20s', interface='eth0'))
    engine.generateNetworkLoad(GenerateNetworkLoadEvent(action="network_load", src_device_type = "poa", src_device_name = "poa5", time='100s', interface='eth0', load='30mb'))
    engine.migrateDevice(MigrateEvent(action="migrate", src_device_type = "ues", src_device_name = "ue5", dst_device_type = "serversd", dst_device_name = "svr1", time='300s', interface='eth0'))

