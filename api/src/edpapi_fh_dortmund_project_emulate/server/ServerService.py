import abc


class ServerService:
    @abc.abstractmethod
    def get_servers(self, app: str | None = None) -> list[str]:
        """
        Gets the list of servers (hostnames) where a particular app is deployed.
        If no app parameter is given, then return the list of all
        servers for what we are collecting metrics

        :param app: optional application name
        :returns: list of server names where the app is running or
            all servers for what metrics are collected.
        """
