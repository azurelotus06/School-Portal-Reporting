import os
import sys
import traceback
import yaml

from scraper import DashboardScraper
from utils import write_csv
from emailer import EmailJSClient
from scheduler import ReportScheduler

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config/config.yaml")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "../dashboard_report.csv")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def send_error_alert(config, error_msg):
    if config.get("send_error_alerts", False):
        emailjs = config["emailjs"]
        client = EmailJSClient(
            emailjs["service_id"],
            emailjs["template_id"],
            emailjs["public_key"]
        )
        recipients = config.get("emails", [])
        for email in recipients:
            try:
                client.send_csv_report(
                    [email],
                    csv_path=None,
                    subject="School Portal Reporting Error",
                    body=f"An error occurred:\n\n{error_msg}"
                )
            except Exception as e:
                print(f"Failed to send error alert to {email}: {e}")

def generate_and_send_report():
    config = load_config()
    scraper = DashboardScraper(CONFIG_PATH)
    try:
        data = scraper.scrape_dashboard()
        write_csv(data, OUTPUT_CSV)
        emailjs = config["emailjs"]
        client = EmailJSClient(
            emailjs["service_id"],
            emailjs["template_id"],
            emailjs["public_key"]
        )
        recipients = config.get("emails", [])
        client.send_csv_report(recipients, OUTPUT_CSV)
        print("Report generated and emailed successfully.")
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error: {e}\n{tb}")
        send_error_alert(config, f"{e}\n{tb}")
    finally:
        scraper.close()

def main():
    config = load_config()
    scheduler = ReportScheduler(
        report_func=generate_and_send_report,
        timezone=config.get("timezone", "America/Chicago"),
        report_time=config.get("report_time", "08:00")
    )
    scheduler.print_current_time()
    if len(sys.argv) > 1 and sys.argv[1] == "now":
        generate_and_send_report()
    else:
        scheduler.start()

if __name__ == "__main__":
    main()
