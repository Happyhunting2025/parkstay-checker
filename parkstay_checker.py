import os
import time
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# =========================================================
# CONFIGURATION
# =========================================================

SITE_ID = int(os.getenv("SITE_ID", 147))
ARRIVAL_DATE = os.getenv("ARRIVAL_DATE", "2026/05/05")
DEPARTURE_DATE = os.getenv("DEPARTURE_DATE", "2026/05/06")
NUM_ADULTS = int(os.getenv("NUM_ADULTS", 2))
NUM_CHILDREN = int(os.getenv("NUM_CHILDREN", 0))
NUM_INFANTS = int(os.getenv("NUM_INFANTS", 0))
NUM_CONCESSION = int(os.getenv("NUM_CONCESSION", 0))
GEAR_TYPE = os.getenv("GEAR_TYPE", "all")

EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# =========================================================
# PARKSTAY URL BUILDER
# =========================================================

PARKSTAY_URL = (
    "https://parkstay.dbca.wa.gov.au/search-availability/campground/"
    f"?site_id={SITE_ID}"
    f"&num_adult={NUM_ADULTS}"
    f"&num_concession={NUM_CONCESSION}"
    f"&num_children={NUM_CHILDREN}"
    f"&num_infants={NUM_INFANTS}"
    f"&gear_type={GEAR_TYPE}"
    f"&arrival={ARRIVAL_DATE.replace('/', '%2F')}"
    f"&departure={DEPARTURE_DATE.replace('/', '%2F')}"
)

# =========================================================
# SELENIUM DRIVER
# =========================================================

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

# =========================================================
# AVAILABILITY CHECK
# =========================================================

def check_availability(driver):
    try:
        print("Loading ParkStay page...")
        driver.get(PARKSTAY_URL)
        time.sleep(6)  # allow JS to load

        print("Checking for enabled 'Book' buttons...")

        # Find ALL button elements that contain "Book"
        book_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Book')]")

        if not book_buttons:
            print("No 'Book' buttons found on page — likely no availability.")
            return False

        for btn in book_buttons:
            try:
                if btn.is_enabled() and btn.is_displayed():
                    print("Found ENABLED BOOK BUTTON → availability likely.")
                    return True
            except:
                continue

        print("All 'Book' buttons are disabled or hidden — no availability.")
        return False

    except Exception as e:
        print(f"Error during availability check: {e}")
        return False

# =========================================================
# EMAIL SENDER
# =========================================================

def send_email_notification():
    subject = "Parks WA Campsite Available!"
    body = f"A campsite may now be available! Check here:\n\n{PARKSTAY_URL}"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        print(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USERNAME"), EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"[{datetime.now()}] Email sent to {EMAIL_TO}")

    except Exception as e:
        print(f"[{datetime.now()}] Failed to send email: {e}")

# =========================================================
# MAIN EXECUTION
# =========================================================

driver = setup_driver()
availability = check_availability(driver)
driver.quit()

if availability:
    print("Campsite MAY be available!")
    send_email_notification()
else:
    print("No availability for these dates.")
