class PlatformModuleObject():
    """
    ConsoleModuleObject is a PlatformObject that is used to represent a console object in the console.
    """
 
    def __init__(self,  name: str):
        """
        Creates a new ConsoleModuleObject
        :param owner_module: Owner module of this object
        :param name: Name of the object
        """

        self._name = name
