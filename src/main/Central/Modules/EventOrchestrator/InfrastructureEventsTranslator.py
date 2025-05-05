import os
import sys
from queue import Queue

from fabric import Result  # type: ignore

from ModuleManagement.DataModels.event import StressEvent, CpuLoadEvent, MemoryLoadEvent, SshEvent
from ModuleManagement.console import output_to_console

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from Modules.EventOrchestrator.InfrastructureEventsRequester import InfrastructureEventsRequester



class InfrastructureEventInterpreter():


    def __init__(self):
        
        self.infr_event_queue= Queue[StressEvent | SshEvent](maxsize = 3)
        self._inf_translator_engine_ = InfrastructureEventsTranslator()
        self.INFRASTRUCTURE_EVENT_ACTIONS = ["cpu_load", "memory_load", 'ssh']
        # all commands related to network should be declared here
        # TODO: can get rid of INFRASTRUCTURE_EVENT_ACTIONS, but it is used for validation in the main module


    def interpret_event(self, event: StressEvent | SshEvent):
        """
        Interpret the event and return the corresponding command
        """
        try:
            if isinstance(event, SshEvent):
                try:
                    print(event)
                    r = self._inf_translator_engine_.do_ssh(event)
                    print(r)
                    output_to_console(r.connection.host, f'{r.command} outputs {r.stdout} {r.stderr}')
                except Exception as err:
                    output_to_console(event.src_device_name, err)
            elif isinstance(event, CpuLoadEvent):
                self._inf_translator_engine_.generateCPULoad(event)
            elif isinstance(event, MemoryLoadEvent):
                self._inf_translator_engine_.generateMemoryLoad(event)
            else:
                # Handle the case when action is not found
                print (f"Unknown action: {event.action}")

        except Exception as e:
            print(f"Missing Parameter: {e}")
    

    def infrastructureEventInterpreter_runner(self):
        """ 
        Run a thread to listen to the event queue. When an event arrives, interpret it and run the
        corresponding method.
        """
        while True:
            event = self.infr_event_queue.get()
            #print("forwarding event {}, to infrastructure".format(event))
            self.interpret_event(event)



class InfrastructureEventsTranslator():


    def __init__(self) -> None:
        self._devices_ = ["server", "ue"]
        self._requester_: dict[str, InfrastructureRequests] = {}
                
        try :
            for device in self._devices_:
                device_lower = device.lower()

                if device_lower in self._devices_:
                    requester_class: type[InfrastructureRequests] = {
                        "server": ServerInfrastructureRequests,
                        "ue": UserEquipmentInfrastructureRequests,
                    }[device_lower]
                    self._requester_[device] = requester_class()
        except:
            print ("INFRASTRUCTURE EVENT: Device configuration file not found")


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
            print ("INFRASTRUCTURE EVENT: Device type is not accepted")
        return False


    def generateCPULoad(self, event: CpuLoadEvent):
        """
        Generates CPU load in a given device

        Parameters:
        src_device_type (str): The type of the source device.
        src_device_name (str): The name of the source device.
        cores (int): The number of cores where to generate the load. 0 means all.
        load (int): The amount of load to generate in each core.
        time (str): The time the network load should be generated, ending in s,m,h second/minute/hour
        
        Returns:
        None
        """ 
        if self.validateDevice(event.src_device_type):
            requester = self._requester_[event.src_device_type] if event.src_device_type else None
            if isinstance(requester, ServerInfrastructureRequests):
                requester.generateCPULoadInServer(event)
            elif isinstance(requester, UserEquipmentInfrastructureRequests):
                requester.generateCPULoadInUE(event)
            # Add more conditions for other device types if needed
        else:
            print(f"INFRASTRUCTURE EVENT:Invalid device type: {event.src_device_type}")


    def generateMemoryLoad(self, event: MemoryLoadEvent):
        """
        Generates Network load in a given device

        Parameters:
        src_device_type (str): The type of the source device.
        src_device_name (str): The name of the source device.
        workers (int): The number of workers used to generate the load.
        load (int): The amount of memory load to generate.
        time (str): The time the network load should be generated, ending in s,m,h second/minute/hour
        
        Returns:
        None
        """ 
        if self.validateDevice (event.src_device_type):
            requester = self._requester_[event.src_device_type] if event.src_device_type else None
            if isinstance(requester, ServerInfrastructureRequests):
                requester.generateMemoryLoadInServer(event)
            elif isinstance(requester, UserEquipmentInfrastructureRequests):
                requester.generateMemoryLoadInUE(event)
            # Add more conditions for other device types if needed
        else:
            print(f"INFRASTRUCTURE EVENT:Invalid device type: {event.src_device_type}")

    def do_ssh(self, event: SshEvent) -> Result | None:
        requester = self._requester_[event.src_device_type] if event.src_device_type else None
        return requester.do_ssh(event) if requester else None


class InfrastructureRequests:
    def __init__(self) -> None:
        self._requester_ = InfrastructureEventsRequester()

    def do_ssh(self, event: SshEvent) -> Result:
        return self._requester_.do_ssh(event)


class UserEquipmentInfrastructureRequests(InfrastructureRequests):
    def generateCPULoadInUE(self, event: CpuLoadEvent) -> None:
        print(f"INFRASTRUCTURE EVENT:Generate {event.cores} CPU {event.load} % load in ue:{event.src_device_name} for {event.time}")
        self._requester_.requestCPULoadUE(event)

    def generateMemoryLoadInUE(self, event: MemoryLoadEvent) -> None:
        print(f"INFRASTRUCTURE EVENT:Generate Memory {event.workers} workers with {event.load} load in ue:{event.src_device_name} for {event.time}")
        self._requester_.requestMemoryLoadUE(event)


class ServerInfrastructureRequests(InfrastructureRequests):
    def generateCPULoadInServer(self, event: CpuLoadEvent) -> None:
        print(f"INFRASTRUCTURE EVENT:Generate {event.cores} CPU {event.load} % load in ue:{event.src_device_name} for {event.time}")
        self._requester_.requestCPULoadServer(event)

    def generateMemoryLoadInServer(self, event: MemoryLoadEvent) -> None:
        print(f"INFRASTRUCTURE EVENT:Generate Memory {event.workers} workers with {event.load} load in server:{event.src_device_name} for {event.time}")
        self._requester_.requestMemoryLoadServer(event)





if __name__ == "__main__":

    engine = InfrastructureEventsTranslator()
    engine.generateCPULoad(CpuLoadEvent(action="cpu_load", src_device_type = "ue", src_device_name = "ue1", cores = 5, load = '100', time='20s'))
    engine.generateMemoryLoad(MemoryLoadEvent(action="memory_load", src_device_type = "server", src_device_name = "svr1", workers = 2, load = '88'))
 