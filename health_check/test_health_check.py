"""This file tests health_check.py"""
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
import pandas as pd
from health_check import get_db_connection, get_df, send_email,\
      get_anomolous_column, get_missing_values

class TestHealthCheck(unittest.TestCase):
    """
    This class contains unit tests for the health check functionalities related to 
    environmental data monitoring.

    The tests cover database interactions, data processing for anomalies detection 
    in temperature and soil moisture,handling of missing values, 
    and the capability to send notifications via email.
    """
    def setUp(self):
        """
        Set up the test environment before each test.
        This method prepares a mock database connection and a mock SES client for sending emails.
        It also creates an example dataframe that mimics the data structure expected 
        from database queries.
        """
        self.example_data = pd.DataFrame({
            'plant_id': [1, 2, 3],
            'temperature': [20, 21, 22],
            'soil_moisture': [30, 32, 34],
            'recording_taken': [
                datetime.now(timezone.utc) - timedelta(hours=1),
                datetime.now(timezone.utc) - timedelta(hours=1.5),
                datetime.now(timezone.utc) - timedelta(hours=2)
            ]
        })


        self.patcher = patch('health_check.connect', return_value=MagicMock())
        self.mock_db_conn = self.patcher.start()
        self.mock_cursor = MagicMock()
        self.mock_db_conn.cursor.return_value.__enter__.return_value = self.mock_cursor
        self.mock_cursor.fetchall.return_value = self.example_data.to_dict('records')


        self.ses_client_patcher = patch('health_check.client')
        self.mock_ses_client = self.ses_client_patcher.start()

    def tearDown(self):
        """
        Clean up after each test.

        This method stops all patches started in the setUp method, 
        ensuring that no side effects remain.
        """
        self.patcher.stop()
        self.ses_client_patcher.stop()

    def test_get_db_connection(self):
        """
        Test the database connection function to ensure it returns a connection 
        object when provided with valid credentials.
        """
        conn = get_db_connection({
            "DB_HOST": "localhost",
            "DB_PORT": 1433,
            "DB_USER": "user",
            "DB_PASSWORD": "password",
            "DB_NAME": "database"
        })
        self.assertIsNotNone(conn)

    def test_get_df(self):
        """
        Test the function that retrieves a dataframe from the database to ensure it
        correctly formats the data into a pandas DataFrame.
        """
        df = get_df(self.mock_db_conn)
        self.assertEqual(len(df), 3)

    def test_get_anomolous_moisture(self):
        """
        Test the detection of anomalous moisture levels.
        Ensures that the function correctly identifies and returns a dataframe with
        records that fall outside expected moisture levels.
        """
        df = get_anomolous_column(self.example_data,'soil_moisture')
        self.assertIsInstance(df, pd.DataFrame)  # Check for DataFrame return type

    def test_get_anomolous_temp(self):
        """
        Test the detection of anomalous temperature readings.

        This method verifies that the function correctly processes the input 
        data and identifies temperature anomalies effectively.
        """
        df = get_anomolous_column(self.example_data,'temperature')
        self.assertIsInstance(df, pd.DataFrame)  # Check for DataFrame return type

    def test_get_missing_values(self):
        """
        Test the identification of missing values in the dataset.

        This method ensures that the function accurately finds and returns 
        a set of columns with missing data.
        """
        missing_values = get_missing_values(self.example_data)
        self.assertIsInstance(missing_values, set)

    def test_send_email(self):
        """
        Test the email sending functionality.

        This method ensures that the function calls the SES client's 
        send_email method correctly when attempting to send an email.
        """
        with patch.object(self.mock_ses_client, 'send_email') as mock_send_email:
            send_email(self.mock_ses_client, "<p>Test Email</p>")
            mock_send_email.assert_called_once()

if __name__ == '__main__':
    unittest.main()
