import os
import sys
from queue import Queue

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from ModuleManagement.PlatformModuleSingletonObject import SingletonInterface


class CommandTranslatorModuleObject(SingletonInterface):

    _instance = None
    @staticmethod
    def get_instance():
        if CommandTranslatorModuleObject._instance is None:
            CommandTranslatorModuleObject._instance = CommandTranslatorModuleObject()
        return CommandTranslatorModuleObject._instance
    
    
    def __init__(self):
               
         self.translation_event_queue= Queue(maxsize = 3) 
