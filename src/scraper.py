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

    def _add_courses_to_config(self, new_courses, config_path: str = "config/config.yaml"):
        """
        Adds each course in `new_courses` (list or set) as `course_name: true` above '# Add more courses as needed'.
        """
        if not new_courses:
            return
        with open(config_path, "r") as f:
            lines = f.readlines()

        # Locate courses section and insertion point
        course_section_idx = None
        insert_idx = None
        for idx, line in enumerate(lines):
            if line.strip() == "courses:":
                course_section_idx = idx
            if "# Add more courses as needed" in line:
                insert_idx = idx
                break

        if course_section_idx is not None and insert_idx is not None:
            # Prepare a set of existing course names in config
            course_lines = lines[course_section_idx+1:insert_idx]
            existing = set(l.split(':', 1)[0].strip() for l in course_lines if ':' in l)

            insert_lines = [f"  {name}: true\n" for name in new_courses if name not in existing]
            if insert_lines:
                # Insert all new courses above the comment
                for offset, il in enumerate(insert_lines):
                    lines.insert(insert_idx + offset, il)
                with open(config_path, "w") as f:
                    f.writelines(lines)
                    
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

        # **SWITCH BACK TO DEFAULT CONTENT (this is critical!)**
        self.driver.switch_to.default_content()

        # Wait for dashboard header text after login
        wait.until(
            EC.presence_of_element_located((By.XPATH, '//h2[contains(@class, "border-bottom") and contains(text(),"Dashboard")]'))
        )
        # TODO: Add error handling for failed login

    def scrape_dashboard(self) -> List[Dict[str, Any]]:
        import datetime

        self.login()
        self.driver.get(self.DASHBOARD_URL)
        time.sleep(2)
        data = []
        missing_courses = []

        # Get student tabs (if multiple students)
        student_tabs = self.driver.find_elements(By.CSS_SELECTOR, "ul#nav2 li a")
        num_tabs = len(student_tabs)
        for tab_idx in range(num_tabs):
            # Get fresh tabs each iteration because DOM may reload
            student_tabs = self.driver.find_elements(By.CSS_SELECTOR, "ul#nav2 li a")
            tab = student_tabs[tab_idx]  # this ref is fresh

            student_name = tab.text.strip()
            tab.click()
            time.sleep(2)

            # Find all course cards
            course_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.col-lg-4.col-xl-4.mb-3')
            for card in course_cards:
                try:
                    # Course Name
                    course_name_elem = card.find_element(By.CSS_SELECTOR, ".card-title")
                    course_name = course_name_elem.text.strip()
                    
                    # Collect missing courses, don't immediately update config
                    if course_name not in self.config["courses"]:
                        missing_courses.insert(0, course_name)

                    # Filter by config
                    if not self.config["courses"].get(course_name, True):
                        continue

                    # Course Period
                    period_elem = card.find_element(By.CSS_SELECTOR, "small.text-muted")
                    course_period = period_elem.text.strip()

                    # Current Grade (%)
                    try:
                        grade_elem = card.find_element(By.CSS_SELECTOR, ".card-grade")
                        current_grade = grade_elem.text.replace("%", "").replace(" ", "").strip()
                    except Exception:
                        current_grade = ""

                    # Current Grade Level (Letter, per rubric)
                    try:
                        grade_num = float(current_grade)
                        if grade_num < 70:
                            current_grade_level = "F"
                        elif 70 <= grade_num < 75:
                            current_grade_level = "D"
                        elif 75 <= grade_num < 80:
                            current_grade_level = "C"
                        elif 80 <= grade_num < 90:
                            current_grade_level = "B"
                        elif grade_num >= 90:
                            current_grade_level = "A"
                        else:
                            current_grade_level = ""
                    except Exception:
                        current_grade_level = ""

                    # Total Assignments, Expected, Completed, Overdue
                    actual_assignments = ""
                    expected_assignments = ""
                    completed_assignments = ""
                    overdue_assignments = ""
                    try:
                        actual_elem = card.find_element(By.XPATH, ".//span[contains(@class,'progress-mark-tooltip-label') and contains(text(), 'Actual')]/following-sibling::span//label")
                        actual_text = actual_elem.text.strip()  # e.g., "2 of 2"
                        if "of" in actual_text:
                            completed_assignments, actual_assignments = [s.strip() for s in actual_text.split("of", 1)]
                        else:
                            completed_assignments = actual_text.strip()
                            actual_assignments = ""
                    except Exception:
                        pass
                    try:
                        # Grab the "expected" line (e.g., "10 of 40")
                        expected_elem = card.find_element(
                            By.XPATH,
                            ".//span[contains(@class, 'progress-mark-tooltip expected')]" +
                            "/span[contains(@class, 'progress-mark-tooltip-container')]" +
                            "/span[contains(@class, 'progress-mark-tooltip-content')]"
                        )
                        expected_text = expected_elem.text.strip()  # e.g. "10 of 40"
                        if "of" in expected_text:
                            expected_assignments = expected_text.split("of")[0].strip()
                        else:
                            # fallback if not in expected format
                            expected_assignments = expected_text.strip()
                    except Exception as e:
                        print(f"[ERROR] Failed to get expected_assignments: {e}")
                        expected_assignments = ""
                        return
                    try:
                        overdue_assignments = str(int(expected_assignments) - int(completed_assignments))
                    except Exception:
                        overdue_assignments = ""

                    # Minutes Spent
                    try:
                        min_elem = card.find_element(
                            By.XPATH,
                            './/div[contains(@class, "text-right") and contains(., "min")]'
                        )
                        minutes_spent = min_elem.text.replace("min", "").strip()
                    except Exception:
                        minutes_spent = ""

                    # Days Left
                    try:
                        days_elem = card.find_element(
                            By.XPATH,
                            './/div[contains(@class,"align-self-center")][contains(., "left")]'
                        )
                        days_left = (
                            days_elem.text.replace("left", "")
                            .replace("d", "")
                            .strip()
                        )
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
                        "Expected Assignments": expected_assignments,
                        "Completed Assignments": completed_assignments,
                        "Overdue Assignments": overdue_assignments,
                        "Minutes Spent": minutes_spent,
                        "Days Left": days_left,
                        "Class Status": class_status,
                        "Report Date": report_date
                    })
                except Exception:
                    continue
        # At the END (right before return), update the yaml ONCE
        if missing_courses:
            self._add_courses_to_config(set(missing_courses), "config/config.yaml")
            # Also update in-memory config
            for c in set(missing_courses):
                self.config["courses"][c] = True
        print(data)
        return data

    def close(self):
        if self.driver:
            self.driver.quit()
