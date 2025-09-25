import requests
import base64
from typing import List

class EmailJSClient:
    """
    Sends emails with CSV reports using the EmailJS REST API.
    """

    API_URL = "https://api.emailjs.com/api/v1.0/email/send"

    def __init__(self, service_id: str, template_id: str, public_key: str):
        self.service_id = service_id
        self.template_id = template_id
        self.public_key = public_key

    def send_csv_report(self, recipients: List[str], csv_path: str, subject: str = "Student Dashboard Report", body: str = "See attached CSV report."):
        # Read and encode CSV as base64
        with open(csv_path, "rb") as f:
            csv_bytes = f.read()
            csv_b64 = base64.b64encode(csv_bytes).decode("utf-8")

        for email in recipients:
            payload = {
                "service_id": self.service_id,
                "template_id": self.template_id,
                "user_id": self.public_key,
                "template_params": {
                    "to_email": email,
                    "subject": subject,
                    "message": body
                },
                "attachments": [
                    {
                        "name": "dashboard_report.csv",
                        "data": f"data:text/csv;base64,{csv_b64}"
                    }
                ]
            }
            resp = requests.post(self.API_URL, json=payload)
            if resp.status_code != 200:
                print(f"Failed to send email to {email}: {resp.text}")
            else:
                print(f"Email sent to {email}")
