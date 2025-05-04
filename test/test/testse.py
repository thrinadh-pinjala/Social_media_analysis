import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from your_flask_app import send_bp  # Replace with your actual Flask Blueprint import

# Create a test Flask app
def create_test_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(send_bp)
    return app

# Real Test Cases
class TestScheduleReport(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        self.client = self.app.test_client()

    @patch('your_flask_app.current_app.extensions')
    def test_happy_path(self, mock_extensions):
        """Test the endpoint with valid input data."""
        # Mock the email sending function
        mock_mail = MagicMock()
        mock_extensions.__getitem__.return_value = mock_mail

        # Test data
        data = {
            "email": "test@example.com",
            "reportType": "Monthly Report",
            "scheduleTime": "2023-12-01T10:00:00",
            "format": "PDF"
        }

        # Make the request
        response = self.client.post("/schedule-report", json=data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Report scheduled successfully")
        mock_mail.send.assert_called_once()

    def test_missing_fields(self):
        """Test the endpoint with missing required fields."""
        # Test data
        data = {
            "email": "test@example.com",
            "reportType": "Monthly Report"
        }

        # Make the request
        response = self.client.post("/schedule-report", json=data)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Missing required fields")

    def test_invalid_email_format(self):
        """Test the endpoint with an invalid email format."""
        # Test data
        data = {
            "email": "invalid-email",
            "reportType": "Monthly Report",
            "scheduleTime": "2023-12-01T10:00:00",
            "format": "PDF"
        }

        # Make the request
        response = self.client.post("/schedule-report", json=data)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Invalid email format")

    def test_empty_request_body(self):
        """Test the endpoint with an empty request body."""
        # Test data
        data = {}

        # Make the request
        response = self.client.post("/schedule-report", json=data)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "No data received")

    @patch('your_flask_app.current_app.extensions')
    def test_email_sending_failure(self, mock_extensions):
        """Test the endpoint when email sending fails."""
        # Mock the email sending function to raise an exception
        mock_mail = MagicMock()
        mock_mail.send.side_effect = Exception("SMTP server error")
        mock_extensions.__getitem__.return_value = mock_mail

        # Test data
        data = {
            "email": "test@example.com",
            "reportType": "Monthly Report",
            "scheduleTime": "2023-12-01T10:00:00",
            "format": "PDF"
        }

        # Make the request
        response = self.client.post("/schedule-report", json=data)

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Failed to send email: SMTP server error")

    def test_invalid_schedule_time_format(self):
        """Test the endpoint with an invalid schedule time format."""
        # Test data
        data = {
            "email": "test@example.com",
            "reportType": "Monthly Report",
            "scheduleTime": "invalid-time",
            "format": "PDF"
        }

        # Make the request
        response = self.client.post("/schedule-report", json=data)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Invalid schedule time format")

    def test_unsupported_report_format(self):
        """Test the endpoint with an unsupported report format."""
        # Test data
        data = {
            "email": "test@example.com",
            "reportType": "Monthly Report",
            "scheduleTime": "2023-12-01T10:00:00",
            "format": "TXT"
        }

        # Make the request
        response = self.client.post("/schedule-report", json=data)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Unsupported report format")

    def test_large_input_data(self):
        """Test the endpoint with excessively large input data."""
        # Test data
        data = {
            "email": "a" * 1000 + "@example.com",
            "reportType": "A" * 1000,
            "scheduleTime": "2023-12-01T10:00:00",
            "format": "PDF"
        }

        # Make the request
        response = self.client.post("/schedule-report", json=data)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Input data too large")

    @patch('your_flask_app.os.getenv')
    def test_missing_from_email(self, mock_getenv):
        """Test the endpoint when the FROM_EMAIL environment variable is not set."""
        # Mock os.getenv to return None
        mock_getenv.return_value = None

        # Test data
        data = {
            "email": "test@example.com",
            "reportType": "Monthly Report",
            "scheduleTime": "2023-12-01T10:00:00",
            "format": "PDF"
        }

        # Make the request
        response = self.client.post("/schedule-report", json=data)

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Failed to send email: FROM_EMAIL not configured")

    @patch('your_flask_app.current_app.extensions')
    def test_unexpected_server_error(self, mock_extensions):
        """Test the endpoint when an unexpected server error occurs."""
        # Mock the email sending function to raise an unexpected exception
        mock_mail = MagicMock()
        mock_mail.send.side_effect = Exception("Unexpected error occurred")
        mock_extensions.__getitem__.return_value = mock_mail

        # Test data
        data = {
            "email": "test@example.com",
            "reportType": "Monthly Report",
            "scheduleTime": "2023-12-01T10:00:00",
            "format": "PDF"
        }

        # Make the request
        response = self.client.post("/schedule-report", json=data)

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Server error: Unexpected error occurred")

if __name__ == "__main__":
    unittest.main()
    