import abc
import json

import requests  # type: ignore
from requests import Response

from ModuleManagement.DataModels.event import Event
from ModuleManagement.configuration_aware import ConfigurationAware
from ModuleManagement.console import output_to_console


class EventsRequester(ConfigurationAware):

    @abc.abstractmethod
    def _get_endpoint(self, *args) -> str:
        """
        Gets the endpoint of a certain device as declared in the ScenarioConfig.json file

        :param device_type: The type of the device.
        :param device_name: The name of the device.
        :param device_action: The action to implement in the device. Must be included in the json file into "paths"

        Returns:
        The generated endpoint
        """

    def post(self, *args, data: dict | None = None, headers: dict | None = None, event: Event | None = None) -> Response | None:
        """
        Executes a POST request towards url resolved by _get_endpoint method
        using the given *args

        :param *args: argugemts for the _get_endpoint method
        :param data: POST request json payload
        :param headers: POST request headers
        :param event: associated stress event object

        :returns: http response
        """
        # Define the headers
        if headers is None:
            headers = {}
        if data is None:
            data = {}
        headers.update({'Content-Type': 'application/json'})
        if event:
            data.update(event.payload())
        # Convert the data to a JSON string
        body_json = json.dumps(data)
        endpoint = self._get_endpoint(*args)
        output_to_console('event-orchestrator', f'posting {body_json} to {endpoint}')
        try:
            response = requests.post(endpoint, headers=headers, data=body_json)
            output_to_console(endpoint, str(response))
            return response
        except Exception as err:
            output_to_console(endpoint, err)
        return None
