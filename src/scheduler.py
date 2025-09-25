from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import time

class ReportScheduler:
    """
    Schedules the dashboard report to run daily at a specified time and timezone.
    """

    def __init__(self, report_func, timezone: str, report_time: str):
        """
        :param report_func: Callable to run for the report (no args)
        :param timezone: Timezone string (e.g., 'America/Chicago')
        :param report_time: Time in 'HH:MM' 24h format (local to timezone)
        """
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
        """
        Run the report immediately (on-demand).
        """
        self.report_func()
