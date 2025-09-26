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
    return

def generate_and_send_report():
    import collections

    config = load_config()
    scraper = DashboardScraper(CONFIG_PATH)
    try:
        data = scraper.scrape_dashboard()
        # Group data by student name
        students = collections.defaultdict(list)
        for row in data:
            students[row["Student Name"]].append(row)

        # Ensure reports directory exists
        reports_dir = os.path.join(os.path.dirname(__file__), "../reports")
        os.makedirs(reports_dir, exist_ok=True)

        emailjs = config["emailjs"]
        client = EmailJSClient(
            emailjs["service_id"],
            emailjs["template_id"],
            emailjs["public_key"]
        )

        for student_name, student_data in students.items():
            # Write CSV for this student
            safe_name = student_name.replace(" ", "_")
            csv_path = os.path.join(reports_dir, f"{safe_name}.csv")
            write_csv(student_data, csv_path)

            # Calculate grade_summary (bulleted, multi-line format)
            from collections import defaultdict
            grade_map = defaultdict(list)
            for row in student_data:
                grade = row.get("Current Grade Level", "")
                course = row.get("Course Name", "")
                if grade and course:
                    grade_map[grade].append((course))
            grade_order = ["A", "B", "C", "D", "F"]
            summary_lines = []
            for grade in grade_order:
                courses = grade_map.get(grade, [])
                if courses:
                    summary_lines.append(f"({len(courses)}) {grade}")
                    for course in courses:
                        summary_lines.append(f"- {course}")
            grade_summary = "\n".join(summary_lines)

            # Calculate total_assignments and total_past_due
            def safe_int(val):
                try:
                    v = int(val)
                    return v if v > 0 else 0
                except Exception:
                    return 0
            total_assignments = sum(safe_int(row.get("Expected Assignments", 0)) for row in student_data)
            total_past_due = sum(safe_int(row.get("Overdue Assignments", 0)) for row in student_data)

            # Get emails for this student
            emails_dict = config.get("emails", {})
            recipients = emails_dict.get(student_name, [])
            if not recipients:
                print(f"No emails found for student: {student_name}, skipping email.")
                continue

            # Send email with CSV and new template params
            client.send_csv_report(
                csv_path,
                recipients,
                student_name,
                grade_summary=grade_summary,
                total_assignments=str(total_assignments),
                total_past_due=str(total_past_due)
            )
            print(f"Report for {student_name} generated and emailed to: {', '.join(recipients)}")

        print("All student reports generated and emailed successfully.")
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
