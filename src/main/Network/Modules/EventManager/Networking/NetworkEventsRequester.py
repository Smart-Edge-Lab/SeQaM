import os
import sys

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Network")[0]
sys.path.insert(0, ROOT_PATH)

from ModuleManagement.DataModels.event import GenerateNetworkLoadEvent, ChangeBandwidthEvent
from Modules.EventManager.Networking.Implementer.NetworkImplementer import NetworkBandwidthImplementer, NetworkLoadImplementer



class NetworkEventsRequester():
    def __init__(self):
        self._badwidth_handler_ = NetworkBandwidthImplementer()
        self._load_handler_ = NetworkLoadImplementer()

    def requestBandwidthEvent(self, event_body: ChangeBandwidthEvent):
        print("DISTRIBUTED NETWORK EVENT: BANDWIDTH", event_body )
        self._badwidth_handler_.invoke_network_bandwidth(event_body)

    def requestNetworkLoadEvent(self, event_body: GenerateNetworkLoadEvent):
        print("DISTRIBUTED NETWORK EVENT: LOAD", event_body)
        self._load_handler_.invoke_network_load(event_body)

