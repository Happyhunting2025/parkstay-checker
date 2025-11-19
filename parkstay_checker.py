import os
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =========================================================
# CONFIGURATION (environment variables override these)
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
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")

# Convert 2026/05/05 → 2026-05-05
ARRIVAL_FORMATTED = ARRIVAL_DATE.replace("/", "-")
DEPARTURE_FORMATTED = DEPARTURE_DATE.replace("/", "-")


# =========================================================
# API URL
# =========================================================

API_URL = (
    "https://parkstay.dbca.wa.gov.au/api/v1/site_availability"
    f"?site_id={SITE_ID}"
    f"&arrival={ARRIVAL_FORMATTED}"
    f"&departure={DEPARTURE_FORMATTED}"
    f"&gear_type={GEAR_TYPE}"
    f"&adults={NUM_ADULTS}"
    f"&children={NUM_CHILDREN}"
    f"&infants={NUM_INFANTS}"
    f"&concession={NUM_CONCESSION}"
)


# =========================================================
# CHECK AVAILABILITY FROM JSON API
# =========================================================

def check_availability():
    print(f"Requesting availability: {API_URL}")

    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"API request error: {e}")
        return False

    try:
        data = response.json()
    except:
        print("Error decoding JSON.")
        return False

    if "availability" not in data:
        print("API returned no availability field.")
        return False

    avail_list = data["availability"]

    # Look for ANY date showing as available
    for day in avail_list:
        date = day.get("date")
        available = day.get("bookable") or day.get("is_available") or False

        print(f"Date {date} - Available: {available}")

        if available:
            return True

    return False


# =========================================================
# EMAIL SENDER
# =========================================================

def send_email_notification():
    subject = "Parks WA Campsite Available!"
    body = (
        "A campsite is available at Parks WA!\n\n"
        f"Check availability here:\n"
        f"https://parkstay.dbca.wa.gov.au/search-availability/campground/?site_id={SITE_ID}"
        f"&arrival={ARRIVAL_DATE}&departure={DEPARTURE_DATE}"
    )

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        print(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT} as {EMAIL_FROM}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully.")

    except Exception as e:
        print(f"Email send error: {e}")


# =========================================================
# MAIN EXECUTION
# =========================================================

if __name__ == "__main__":
    available = check_availability()

    if available:
        print("Campsite IS AVAILABLE! Sending email...")
        send_email_notification()
    else:
        print("Campsite NOT available.")
