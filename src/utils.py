import csv
from typing import List, Dict

CSV_HEADER = [
    "Student Name",
    "Course Name",
    "Course Period",
    "Current Grade (%)",
    "Current Grade Level",
    "Total Assignments",
    "Expected Assignments",
    "Completed Assignments",
    "Overdue Assignments",
    "Minutes Spent",
    "Days Left",
    "Class Status",
    "Report Date"
]

def write_csv(data: List[Dict], output_path: str):
    """
    Write dashboard data to CSV in the required format.
    """
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
