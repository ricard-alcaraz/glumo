import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
import keyring
import requests


from glumo.gui import GlumoApp

class TestGlumoApp(unittest.TestCase):
    
    @patch('glumo.api.get_stored_credentials')
    @patch('glumo.gui.GlumoApp.auto_login')
    @patch('glumo.gui.GlumoApp.show_login_prompt')
    def setUp(self, mock_show_login_prompt, mock_auto_login, mock_get_stored_credentials):
        mock_get_stored_credentials.return_value = (None, None)
        self.app = GlumoApp()

    def tearDown(self):
        self.app.destroy()

    @patch('glumo.api.store_credentials')
    @patch('glumo.api.login')
    @patch('glumo.api.get_patient_connections')
    @patch('glumo.api.store_patient_id')
    @patch('glumo.api.store_token')
    def test_login_success(self, mock_store_token, mock_store_patient_id, mock_get_patient_connections, mock_login, mock_store_credentials):
        mock_login.return_value = 'test-token'
        mock_get_patient_connections.return_value = {
            'data': [{'patientId': 'test-patient-id'}]
        }
        
        self.app.show_login_window()
        login_window = self.app.winfo_children()[-1]
        email_entry, password_entry = login_window.winfo_children()[1], login_window.winfo_children()[3]
        email_entry.insert(0, 'test-email')
        password_entry.insert(0, 'test-password')
        
        submit_button = login_window.winfo_children()[5]
        submit_button.invoke()

        mock_store_credentials.assert_called_once_with('test-email', 'test-password')
        mock_login.assert_called_once_with('test-email', 'test-password')
        mock_get_patient_connections.assert_called_once_with('test-token')
        mock_store_patient_id.assert_called_once_with('test-patient-id')
        mock_store_token.assert_called_once_with('test-token')
        self.assertEqual(self.app.is_running, True)

    @patch('glumo.api.get_stored_token')
    @patch('glumo.api.get_stored_patient_id')
    @patch('glumo.api.get_cgm_data')
    def test_fetch_data_success(self, mock_get_cgm_data, mock_get_stored_patient_id, mock_get_stored_token):
        mock_get_stored_token.return_value = 'test-token'
        mock_get_stored_patient_id.return_value = 'test-patient-id'
        mock_get_cgm_data.return_value = {
            'data': {
                'graphData': [
                    {'Timestamp': '07/27/2024 10:00:00 AM', 'ValueInMgPerDl': 100},
                    {'Timestamp': '07/27/2024 11:00:00 AM', 'ValueInMgPerDl': 150}
                ]
            }
        }
        
        self.app.fetch_data()
        self.assertEqual(len(self.app.plot_frame.winfo_children()), 1)
        self.assertIn('Most Recent Value: 150 mg/dL', self.app.most_recent_value_label.cget('text'))

    @patch('glumo.api.get_stored_token')
    @patch('glumo.api.get_stored_patient_id')
    @patch('glumo.api.get_cgm_data')
    def test_fetch_data_no_graph_data(self, mock_get_cgm_data, mock_get_stored_patient_id, mock_get_stored_token):
        mock_get_stored_token.return_value = 'test-token'
        mock_get_stored_patient_id.return_value = 'test-patient-id'
        mock_get_cgm_data.return_value = {'data': {}}

        self.app.fetch_data()
        self.assertEqual(self.app.most_recent_value_label.cget('text'), 'Most Recent Value: N/A')

    @patch('glumo.api.get_stored_token')
    @patch('glumo.api.get_stored_patient_id')
    @patch('glumo.api.get_cgm_data')
    def test_fetch_data_error(self, mock_get_cgm_data, mock_get_stored_patient_id, mock_get_stored_token):
        mock_get_stored_token.return_value = 'test-token'
        mock_get_stored_patient_id.return_value = 'test-patient-id'
        mock_get_cgm_data.side_effect = Exception("API Error")

        self.app.fetch_data()
        self.assertEqual(self.app.most_recent_value_label.cget('text'), 'Most Recent Value: N/A')

    def test_on_closing(self):
        self.app.start_auto_refresh()
        self.app.on_closing()
        self.assertEqual(self.app.is_running, False)

if __name__ == '__main__':
    unittest.main()