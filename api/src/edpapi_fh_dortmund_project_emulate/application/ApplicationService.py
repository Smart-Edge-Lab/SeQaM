import abc
from typing import List


class ApplicationService:

    @abc.abstractmethod
    def get_apps(self) -> List[str]:
        """
        Gets list of monitored application(service) names

        :return: application names
        """
