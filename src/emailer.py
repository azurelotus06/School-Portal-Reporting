import subprocess
import base64
import json
from typing import List
import os

class EmailJSClient:
    """
    Sends emails with CSV reports using the EmailJS Node.js SDK via a subprocess call.
    """

    def __init__(self, service_id: str, template_id: str, public_key: str, private_key: str):
        self.service_id = service_id
        self.template_id = template_id
        self.public_key = public_key
        self.private_key = private_key

    def send_csv_report(self, csv_path: str, recipients: List[str], student_name: str = ""):
        # Read and encode CSV as base64 (if needed for your template)
        with open(csv_path, "rb") as f:
            csv_bytes = f.read()
            csv_b64 = base64.b64encode(csv_bytes).decode("utf-8")

        # Prepare template_params (customize as needed for your EmailJS template)
        template_params = {
            "email": ",".join(recipients),
            "student_name": student_name,
            "csv_base64": csv_b64,
            "csv_filename": os.path.basename(csv_path)
        }

        # Use the first recipient for the to_email field (customize as needed)
        recipient_email = recipients[0] if recipients else ""

        args = [
            "node",
            "send_email.js",
            self.service_id,
            self.template_id,
            recipient_email,
            json.dumps(template_params),
            self.public_key,
            self.private_key
        ]

        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            print("Node.js script output:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Node.js script failed:")
            print(e.stderr)
