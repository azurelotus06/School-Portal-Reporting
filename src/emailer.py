import requests
import base64
from typing import List
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import tempfile

class EmailJSClient:
    """
    Sends emails with CSV reports using the EmailJS REST API.
    """

    API_URL = "https://api.emailjs.com/api/v1.0/email/send"

    def __init__(self, service_id: str, template_id: str, public_key: str):
        self.service_id = service_id
        self.template_id = template_id
        self.public_key = public_key

    def send_csv_report(
        self,
        csv_path: str,
        recipients: List[str],
        student_name: str = "",
        grade_summary: str = None,
        total_assignments: str = None,
        total_past_due: str = None
    ):
        # Read and encode CSV as base64
        with open(csv_path, "rb") as f:
            csv_bytes = f.read()
            csv_b64 = base64.b64encode(csv_bytes).decode("utf-8")

        # Prepare template_params
        template_params = {
            "email": ",".join(recipients),
            "student_name": student_name,
            "csv_content": f"data:text/csv;base64,{csv_b64}"
        }
        if grade_summary is not None:
            template_params["grade_summary"] = grade_summary
        if total_assignments is not None:
            template_params["total_assignments"] = total_assignments
        if total_past_due is not None:
            template_params["total_past_due"] = total_past_due

        # Use the CSV filename for the attachment
        csv_filename = os.path.basename(csv_path)

        payload = {
            "service_id": self.service_id,
            "template_id": self.template_id,
            "user_id": self.public_key,
            "template_params": template_params,
        }

        # Use Selenium to send the POST request via browser JS
        html_content = f"""
        <html>
        <body>
        <script>
        async function sendEmail() {{
            const payload = {payload};
            try {{
                const resp = await fetch("{self.API_URL}", {{
                    method: "POST",
                    headers: {{
                        "Content-Type": "application/json"
                    }},
                    body: JSON.stringify(payload)
                }});
                const text = await resp.text();
                document.body.innerText = "STATUS:" + resp.status + "\\n" + text;
            }} catch (e) {{
                document.body.innerText = "ERROR:" + e;
            }}
        }}
        sendEmail();
        </script>
        </body>
        </html>
        """

        # Write HTML to a temp file
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(html_content)
            temp_html_path = f.name

        # Set up Selenium headless Chrome
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)
        try:
            driver.get("file://" + temp_html_path)
            time.sleep(5)  # Wait for JS to execute
            result = driver.find_element("tag name", "body").text
            if result.startswith("STATUS:200"):
                print(f"Email sent to {','.join(recipients)}")
            else:
                print(f"Failed to send email to {','.join(recipients)}: {result}")
        finally:
            driver.quit()
            os.remove(temp_html_path)
