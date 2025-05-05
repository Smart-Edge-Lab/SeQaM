import os
import sys

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from ModuleManagement.ModuleExecutionException import ModuleExecutionException

class ConsoleException(ModuleExecutionException):
    """
    Signal errors in run-time while executing the console module.
    """

    def __init__(self, message: str, cause: Exception | None = None):
        """
        Constructor of the class
        :param message: Message to be passed to the exception
        :param cause: Cause of the exception (Throwable)
        """
        super().__init__(message)
        self.cause = cause
