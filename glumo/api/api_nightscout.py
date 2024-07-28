import requests
import glumo.config as config
import json
import keyring
import numpy as np
import logging
from glumo.api.base_api import BaseAPI
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class NightscoutAPI(BaseAPI):
    def __init__(self):
        super().__init__()
        self.name = "Nightscout"
        self.base_url = "https://cd4c.ns.gluroo.com/"
        self.headers = ""

    def get_cgm_data(self):
        """Retrieves data from the Nightscout API.
        Args:
            endpoint (str): The endpoint to retrieve data from.
        Returns:
            dict: The data returned by the API.
        """
        url = f"{config.get_base_url('Nightscout')}/api/v1/entries?token={self.get_stored_token()}"
        #headers = {
        #    "Authorization": f"Bearer {config.API_KEY}"
        #}
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def store_token(self, token):
        """Stores the token in the keyring service.
        Args:
            token (str): The token to store.
        """
        keyring.set_password("GlumoApp", "token_nightscout", token)

    def get_stored_token(self):
        """Retrieves the stored token from the keyring service.
        Returns:
            str: The stored token.
        """

        token = keyring.get_password("GlumoApp", "token_nightscout")
        return token
    

    def formatData(self, graph_data):
        """Formats the CGM data.
        Args:
            graph_data (list): The CGM data to format.
        Returns:
            tuple: A tuple containing the formatted CGM data.
        """
        #2024-07-28T08:57:29.000+00:00
        
        timestamp_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        timestamps = [datetime.strptime(entry['sysTime'], timestamp_format) for entry in graph_data]
        values = [entry['sgv'] for entry in graph_data]
        return timestamps, values
    
    def get_last_cgm_value(self, values):
        """Retrieves the last CGM value from the specified list of values.
        Args:
            values (list): The list of values to retrieve the last CGM value from.
        Returns:
            float: The last CGM value.
        """
        last_cgm_value = values[0]
        return last_cgm_value
    
    def login(self):
        super().login()