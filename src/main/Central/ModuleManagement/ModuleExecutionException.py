class ModuleExecutionException(Exception):
    """
    Signal errors in run-time while executing PlatformModule instances.
    """

    def __init__(self, message: str, cause: Exception | None = None):
        """
        Constructor of the class
        :param message: Message to be passed to the exception
        :param cause: Cause of the exception (Throwable)
        """
        super().__init__(message)
        self.cause = cause

