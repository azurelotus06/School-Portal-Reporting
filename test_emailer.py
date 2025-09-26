from src.emailer import EmailJSClient

client = EmailJSClient("service_l9fh0pj", "template_rerp7v6", "ta5OfAVP6Jqpb5VCc")
csv_path = "reports/Noah_Cooksey.csv"
recipients = ["davidgundaker3@gmail.com"]
student_name = "Test Student"
client.send_csv_report(csv_path, recipients, student_name)