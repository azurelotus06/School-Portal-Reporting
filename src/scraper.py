import time
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import yaml

class DashboardScraper:
    """
    Scrapes student dashboard data from laurelsprings.geniussis.com.
    """

    DASHBOARD_URL = "https://laurelsprings.geniussis.com/FEDashboard.aspx"
    LOGIN_URL = "https://laurelsprings.geniussis.com/PublicWelcome.aspx"

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.driver = None

    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _init_driver(self):
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)

    def login(self):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        self._init_driver()
        self.driver.get(self.LOGIN_URL)

        # Wait for the login form to appear (up to 15 seconds)
        wait = WebDriverWait(self.driver, 15)
        
        # Wait for the iframe to appear and switch to it
        iframe = wait.until(EC.presence_of_element_located((By.ID, "iFrameLogin")))
        self.driver.switch_to.frame(iframe)
        
        username = wait.until(
            EC.presence_of_element_located((By.ID, "tbLogin"))
        )
        password = wait.until(
            EC.presence_of_element_located((By.ID, "tbPassword"))
        )
        print(self.config["credentials"]["username"])
        username.send_keys(self.config["credentials"]["username"])
        password.send_keys(self.config["credentials"]["password"])

        # Find and click the login button (by text or type)
        login_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "btLogin"))
        )
        login_btn.click()

        # Wait for dashboard or error message
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Dashboard")]')),
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "MuiPaper-root")]'))
            )
        )
        # TODO: Add error handling for failed login

    def scrape_dashboard(self) -> List[Dict[str, Any]]:
        import datetime

        self.login()
        self.driver.get(self.DASHBOARD_URL)
        time.sleep(2)
        data = []

        # Get student tabs (if multiple students)
        student_tabs = self.driver.find_elements(By.CSS_SELECTOR, ".MuiTabs-flexContainer button")
        for tab in student_tabs:
            tab.click()
            time.sleep(1)
            student_name = tab.text.strip()

            # Find all course cards
            course_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.MuiPaper-root.MuiPaper-elevation1")
            for card in course_cards:
                try:
                    # Course Name
                    course_name_elem = card.find_element(By.CSS_SELECTOR, "div.MuiCardContent-root > div:nth-child(2)")
                    course_name = course_name_elem.text.strip()

                    # Filter by config
                    if not self.config["courses"].get(course_name, False):
                        continue

                    # Course Period
                    period_elem = card.find_element(By.CSS_SELECTOR, "div.MuiCardContent-root > div:nth-child(3)")
                    course_period = period_elem.text.strip()

                    # Current Grade (%)
                    try:
                        grade_elem = card.find_element(By.CSS_SELECTOR, "span[style*='color']")
                        current_grade = grade_elem.text.replace("%", "").strip()
                    except Exception:
                        current_grade = ""

                    # Current Grade Level (not always present, fallback to blank)
                    current_grade_level = ""
                    # (If available, parse from card or elsewhere)

                    # Total Assignments, Expected, Completed, Overdue
                    actual_assignments = ""
                    expected_assignments = ""
                    completed_assignments = ""
                    overdue_assignments = ""
                    try:
                        actual_elem = card.find_element(By.XPATH, ".//div[contains(text(),'Actual')]/following-sibling::div")
                        actual_assignments = actual_elem.text.split("of")[-1].strip()
                        completed_assignments = actual_elem.text.split("of")[0].strip()
                    except Exception:
                        pass
                    try:
                        expected_elem = card.find_element(By.XPATH, ".//div[contains(text(),'Expected')]/following-sibling::div")
                        expected_assignments = expected_elem.text.split("of")[-1].strip()
                    except Exception:
                        pass
                    try:
                        overdue_elem = card.find_element(By.XPATH, ".//div[contains(text(),'Overdue')]/following-sibling::div")
                        overdue_assignments = overdue_elem.text.strip()
                    except Exception:
                        overdue_assignments = ""

                    # Minutes Spent
                    try:
                        min_elem = card.find_element(By.XPATH, ".//span[contains(text(),'min')]")
                        minutes_spent = min_elem.text.replace("min", "").strip()
                    except Exception:
                        minutes_spent = ""

                    # Days Left
                    try:
                        days_elem = card.find_element(By.XPATH, ".//span[contains(text(),'left')]")
                        days_left = days_elem.text.replace("left", "").replace("d", "").strip()
                    except Exception:
                        days_left = ""

                    # Class Status (Active, etc.)
                    class_status = "Active"  # Default, or parse if available

                    # Report Date
                    report_date = datetime.datetime.now().strftime("%-m/%-d/%Y")

                    data.append({
                        "Student Name": student_name,
                        "Course Name": course_name,
                        "Course Period": course_period,
                        "Current Grade (%)": current_grade,
                        "Current Grade Level": current_grade_level,
                        "Total Assignments": actual_assignments,
                        "Expected Assignments by Now": expected_assignments,
                        "Completed Assignments": completed_assignments,
                        "Overdue Assignments": overdue_assignments,
                        "Minutes Spent": minutes_spent,
                        "Days Left": days_left,
                        "Class Status": class_status,
                        "Report Date": report_date
                    })
                except Exception:
                    continue

        return data

    def close(self):
        if self.driver:
            self.driver.quit()
