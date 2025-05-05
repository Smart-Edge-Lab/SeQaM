import os
import sys
import threading
import time


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from ModuleManagement.RestFactory import RestFactory
from Utilities.EndpointGenerator import ModuleEndpointGenerator


#TODO: This class has not been implemented. This should represent the data API component

class DataManagerModuleREST:

    def __init__(self):
        self._factory_ = RestFactory()
        self._endpoint_generator_ = ModuleEndpointGenerator()
        self._module_info_ = self._endpoint_generator_.get_module_info(module_name="Data_Manager")
        self._module_port_ = int(self._module_info_["port"])
        self._metrics_cpu_endpoint_ = self._endpoint_generator_.generate_endpoint(module_name="Data_Manager", module_action="cpu")
        self._metrics_cpu__route = self._metrics_cpu_endpoint_[self._metrics_cpu_endpoint_.find("/",10):]
        self._factory_.create_GET_route(self._metrics_cpu__route, self.handler_metrics_cpu)


    @staticmethod
    def handler_metrics_cpu():
        print("hello from handler" )





if __name__ == '__main__':

    DMRESTEngine = DataManagerModuleREST()

    t3= threading.Thread(target=lambda: DMRESTEngine._factory_.app.run(host='0.0.0.0', port=DMRESTEngine._module_port_, debug=False, use_reloader=False))
    t3.daemon= True
    t3.start()

    while True:
        time.sleep(0.5)