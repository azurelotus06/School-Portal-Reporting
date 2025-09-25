import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import time
from datetime import datetime

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

def report_func():
    print(">>> Report run at:", datetime.now())

class ReportScheduler:
    def __init__(self, report_func, timezone: str, report_time: str):
        self.report_func = report_func
        self.timezone = pytz.timezone(timezone)
        hour, minute = map(int, report_time.split(":"))
        self.scheduler = BackgroundScheduler(timezone=self.timezone)
        self.trigger = CronTrigger(hour=hour, minute=minute, timezone=self.timezone)

    def start(self):
        self.scheduler.add_job(self.report_func, self.trigger, id="daily_report", replace_existing=True)
        self.scheduler.start()
        print("Scheduler started. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()

    def run_now(self):
        self.report_func()

    def print_current_time(self):
        now = datetime.now(self.timezone)
        print(f"Current time in {self.timezone.zone}: {now.strftime('%Y-%m-%d %H:%M:%S')}")