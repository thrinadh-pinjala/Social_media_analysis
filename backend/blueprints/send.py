from flask import Blueprint, request, jsonify
from flask_mail import Message
from flask_cors import CORS
import os
import dotenv
from flask import current_app

# Load environment variables and force override
dotenv.load_dotenv(override=True)

# Create blueprint
send_bp = Blueprint('send', __name__)
CORS(send_bp)
@send_bp.route("/schedule-report", methods=["POST"])
def schedule_report():
    try:
        data = request.json
        print(f"Received data: {data}")  # Debug print

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Extract data from the request
        email = data.get('email')
        report_type = data.get('reportType')
        schedule_time = data.get('scheduleTime')
        format = data.get('format')

        if not email or not report_type or not schedule_time:
            return jsonify({"error": "Missing required fields"}), 400

        # Create the email message
        subject = f"Scheduled Report: {report_type}"
        body = f"""
        Your report '{report_type}' is scheduled for delivery on {schedule_time}.
        
        Report Details:
        - Type: {report_type}
        - Format: {format}
        - Delivery Time: {schedule_time}
        
        You will receive the report at the scheduled time.
        """

        msg = Message(
            subject=subject,
            sender=os.getenv('FROM_EMAIL'),  # Use FROM_EMAIL instead of DEL_EMAIL
            recipients=[email]
        )
        msg.body = body

        try:
            current_app.extensions['mail'].send(msg)
            print(f"Successfully sent confirmation email to {email}")  # Debug print
            return jsonify({
                "message": "Report scheduled successfully",
                "details": {
                    "email": email,
                    "report_type": report_type,
                    "schedule_time": schedule_time
                }
            }), 200
        except Exception as email_error:
            print(f"Email sending failed: {str(email_error)}")  # Debug print
            return jsonify({"error": f"Failed to send email: {str(email_error)}"}), 500

    except Exception as e:
        print(f"Unexpected error in schedule_report: {str(e)}")  # Debug print
        return jsonify({"error": f"Server error: {str(e)}"}), 500