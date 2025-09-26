# School Portal Reporting App

A production-grade Python 3.12 app to automate daily and on-demand student dashboard CSV reports from [Laurel Springs Genius SIS](https://laurelsprings.geniussis.com/), with email delivery via EmailJS.

## Features

- Logs in and scrapes per-student dashboard data (see below for fields)
- Outputs CSV in required format, daily at 8am CT and on-demand
- Configurable course selection (checkbox style) and email recipients
- Sends CSVs to students/parents via EmailJS
- Error alerts via email (optional)
- Modern, maintainable, and robust codebase

## Requirements

- Python 3.12+
- Chrome browser and [ChromeDriver](https://chromedriver.chromium.org/downloads) installed and in PATH
- [UV](https://github.com/astral-sh/uv) for package management (not pip)
- EmailJS account (at least a PERSONAL subscription) with service/template/public key

## Setup

1. **Clone the repo and enter the directory:**
   ```bash
   git clone <your-repo-url>
   cd School-Portal-Reporting
   ```

2. **Use venv for package:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install UV (if not already):**
   ```bash
   pip install uv
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

4. **Configure EmailJS:**
   - Create a free account at [EmailJS](https://www.emailjs.com/).
   - Subscribe plan (at least PERSONAL)
   - Set up an email service and template.
   - Note your service ID, template ID, and public (user) key.

5. **Edit `config/config.yaml` from `config/config.yaml.example` :**
   - Enter your Genius SIS credentials.
   - Set which courses to include (true/false).
   - Add recipient emails.
   - Fill in your EmailJS details.
   - Adjust timezone/report time if needed.

## Usage

- **Run on demand:**
  ```bash
  python src/main.py now
  ```

- **Run as a daily scheduled job (default 8am CT):**
  ```bash
  python src/main.py
  ```
  Leave running (e.g., in a screen/tmux session or as a service).

- **CSV Output:**
  - The CSV is generated in the reports directory.
  - Format:
    ```
    Student Name,Course Name,Course Period,Current Grade (%),Current Grade Level,Total Assignments,Expected Assignments,Completed Assignments,Overdue Assignments,Minutes Spent,Days Left,Class Status,Report Date
    ```
## Checkbox
- The checkbox is checked by default, so if you don't uncheck it, that course will be included in the CSV file.
- You can update on courses.html file.

## Error Handling

- Errors are printed to the console and (optionally) emailed to all recipients if `send_error_alerts: true` in config.

## Troubleshooting

- Ensure Chrome and ChromeDriver are installed and compatible.
- If scraping fails, check for UI changes on the dashboard and update selectors in `src/scraper.py`.
- For EmailJS issues, verify your service/template/public key and template parameters.

## Security

- Never commit your credentials or config with real passwords/keys to version control.
- Use environment variables or secrets management for production deployments.

## License

MIT

---

**For further help, see code comments and docstrings.**
