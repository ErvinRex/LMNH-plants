# health_check_test.py
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime, timedelta, timezone
from health_check import handler, get_db_connection, get_df, send_email, get_anomolous_moisture, get_anomolous_temp, get_missing_values

class TestHealthCheck(unittest.TestCase):
    def setUp(self):
        # Example data that might come from the database
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

        # Mocking database connection and cursor
        self.patcher = patch('health_check.connect', return_value=MagicMock())
        self.mock_db_conn = self.patcher.start()
        self.mock_cursor = MagicMock()
        self.mock_db_conn.cursor.return_value.__enter__.return_value = self.mock_cursor
        self.mock_cursor.fetchall.return_value = self.example_data.to_dict('records')

        # Mock the SES client
        self.ses_client_patcher = patch('health_check.client')
        self.mock_ses_client = self.ses_client_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.ses_client_patcher.stop()

    def test_get_db_connection(self):
        conn = get_db_connection({
            "DB_HOST": "localhost",
            "DB_PORT": 1433,
            "DB_USER": "user",
            "DB_PASSWORD": "password",
            "DB_NAME": "database"
        })
        self.assertIsNotNone(conn)

    def test_get_df(self):
        df = get_df(self.mock_db_conn)
        self.assertEqual(len(df), 3)

    def test_get_anomolous_moisture(self):
        df = get_anomolous_moisture(self.example_data)
        self.assertIsInstance(df, pd.DataFrame)  # Check for DataFrame return type

    def test_get_anomolous_temp(self):
        df = get_anomolous_temp(self.example_data)
        self.assertIsInstance(df, pd.DataFrame)  # Check for DataFrame return type

    def test_get_missing_values(self):
        missing_values = get_missing_values(self.example_data)
        self.assertIsInstance(missing_values, set)

    def test_send_email(self):
        with patch.object(self.mock_ses_client, 'send_email') as mock_send_email:
            send_email(self.mock_ses_client, "<p>Test Email</p>")
            mock_send_email.assert_called_once()



if __name__ == '__main__':
    unittest.main()
