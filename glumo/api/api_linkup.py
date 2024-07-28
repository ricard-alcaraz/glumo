import requests
import glumo.config as config
import keyring
import numpy as np
import logging
from glumo.api.base_api import BaseAPI
from datetime import datetime
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class LinkUPAPI(BaseAPI):

    def __init__(self):
        super().__init__()
        self.name = "LinkUP"
        self.base_url = "https://api-eu.libreview.io"
        self.headers = {
            'accept-encoding': 'gzip',
            'cache-control': 'no-cache',
            'connection': 'Keep-Alive',
            'content-type': 'application/json',
            'product': 'llu.android',
            'version': '4.7'
        }

    def store_credentials(self, email, password):
        """Stores the email and password in the keyring service.
        Args:
            email (str): The email to store.
            password (str): The password to store.
        """
        keyring.set_password("GlumoApp", "email", email)
        keyring.set_password("GlumoApp", "password", password)

    #service_name = "GlumoApp"
    def delete_stored_credentials(self, service_name, username):
        """Deletes the stored credentials for the specified username.
        Args:
            service_name (str): The name of the service to use.
            username (str): The username to delete the credentials for.
        """
        try:
            keyring.delete_password(self, service_name, username)
            logging.debug(f"Credentials for {username} deleted successfully.")
        except keyring.errors.PasswordDeleteError:
            logging.debug(f"No credentials found for {username} to delete.")

    def store_token(self,token):
        """Stores the token in the keyring service.
        Args:
            token (str): The token to store.
        """
        keyring.set_password("GlumoApp", "token", token)

    def get_stored_token(self):
        """Retrieves the stored token from the keyring service.
        Returns:
            str: The stored token.
        """
        token = keyring.get_password("GlumoApp", "token")
        return token

    def store_patient_id(self, patient_id):
        """Stores the patient ID in the keyring service.
        Args:
            patient_id (str): The patient ID to store.
        """
        keyring.set_password("GlumoApp", "patient_id", patient_id)

    def get_stored_patient_id(self):
        """Retrieves the stored patient ID from the keyring service.
        Returns:
            str: The stored patient ID.
        """
        patient_id = keyring.get_password("GlumoApp", "patient_id")
        return patient_id


    def get_stored_credentials(self):
        """Retrieves the stored email and password from the keyring service.
        Returns:
            tuple: A tuple containing the stored email and password.
        """
        email = keyring.get_password("GlumoApp", "email")
        password = keyring.get_password("GlumoApp", "password")
        return email, password

    def login(self):
        """Logs in to the Glumo API using the provided email and password.
        Args:
            email (str): The email to use for login.
            password (str): The password to use for login.
        Returns:
            str: The token returned by the API after successful login.
        """
        endpoint = "/llu/auth/login"
        email, password = self.get_stored_credentials()
        payload = {
            "email": email,
            "password": password
        }
        
        response = requests.post(self.base_url + endpoint, headers=self.headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            token = data.get('data', []).get("authTicket", []).get("token", [])  # Access the "token" key from the response JSON
            self.store_credentials(email, password)
            patient_data = self.get_patient_connections(token)
            patient_id = patient_data['data'][0]["patientId"]
            self.store_patient_id(patient_id)
            self.store_token(token)
        else:
            response.raise_for_status()
        

    # Function to get connections of patients
    def get_patient_connections(self, token):
        """Retrieves the patient connections for the user.
        Args:
            token (str): The token to use for authentication.
        Returns:
            dict: The patient connections data returned by the API.
        """
        endpoint = "/llu/connections"  # This is a placeholder, you'll need to replace with the actual endpoint
        headers = {**self.headers, 'Authorization': f"Bearer {token}"}
        
        response = requests.get(self.base_url + endpoint, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_last_cgm_value(self, values):
        """Retrieves the last CGM value from the specified list of values.
        Args:
            values (list): The list of values to retrieve the last CGM value from.
        Returns:
            float: The last CGM value.
        """
        last_cgm_value = values[-1]
        return last_cgm_value

    # Function to retrieve CGM data for a specific patient
    def get_cgm_data(self):
        """Retrieves the CGM data for the specified patient.
        Args:
            token (str): The token to use for authentication.
            patient_id (str): The patient ID to retrieve the CGM data for.
        Returns:
            dict: The CGM data returned by the API.
        """
        token = self.get_stored_token()
        patient_id = self.get_stored_patient_id()
        endpoint = f"/llu/connections/{patient_id}/graph"  # This is a placeholder, replace with the actual endpoint
        headers = {**self.headers, 'Authorization': f"Bearer {token}"}
        
        response = requests.get(self.base_url + endpoint, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def formatData(self, graph_data):
        """Formats the CGM data.
        Args:
            graph_data (list): The CGM data to format.
        Returns:
            tuple: A tuple containing the formatted CGM data.
        """
        graph_data = graph_data.get('data', {}).get('graphData', [])
        timestamp_format = "%m/%d/%Y %I:%M:%S %p"
        timestamps = [datetime.strptime(entry['Timestamp'], timestamp_format) for entry in graph_data]
        values = [entry['ValueInMgPerDl'] for entry in graph_data]
        return timestamps, values

    # Main Function
    #def main():
    #    email = ""  # Replace with your actual email
    #    password = ""   # Replace with your actual password

    #    token = login(email, password)
    #    patient_data = get_patient_connections(token)
        
    #    patient_id = patient_data['data'][0]["patientId"]
    #    cgm_data = get_cgm_data(token, patient_id)
        
    #    print(cgm_data)

    #if __name__ == "__main__":
    #    main()