import abc


class ServerService:
    @abc.abstractmethod
    def get_servers(self, app: str) -> list[str]:
        """
        Gets the list of servers where a particular app is deployed

        :param app: application name
        :returns: list of server names where the app is running
        """
