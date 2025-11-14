import os 
import time 
import smtplib 
from datetime import datetime 
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart 
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome import ChromeDriverManager 
 
# ========================================================= 
#  CONFIGURATION — change these values if running locally 
# (GitHub Ac ons will override them using secrets) 
# ========================================================= 
 
SITE_ID = int(os.getenv("SITE_ID", 147))              # Campground/site ID 
ARRIVAL_DATE = os.getenv("ARRIVAL_DATE", "2026/02/04") 
DEPARTURE_DATE = os.getenv("DEPARTURE_DATE", "2026/02/05") 
NUM_ADULTS = int(os.getenv("NUM_ADULTS", 2)) 
NUM_CHILDREN = int(os.getenv("NUM_CHILDREN", 0)) 
NUM_INFANTS = int(os.getenv("NUM_INFANTS", 0)) 
NUM_CONCESSION = int(os.getenv("NUM_CONCESSION", 0)) 
GEAR_TYPE = os.getenv("GEAR_TYPE", "all")             # tent, caravan, etc. 
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", 30)) 
 
EMAIL_FROM = os.getenv("EMAIL_FROM", "") 
EMAIL_TO = os.getenv("EMAIL_TO", "") 
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "") 
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com") 
SMTP_PORT = int(os.getenv("SMTP_PORT", 587)) 
 
# ========================================================= 
#  BUILD URL 
# ========================================================= 
PARKSTAY_URL = ( 
    "h ps://parkstay.dbca.wa.gov.au/search-availability/campground/" 
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
#  CORE FUNCTIONS 
# ========================================================= 
 
def setup_driver(): 
    options = Options() 
    options.add_argument("--headless=new") 
    options.add_argument("--disable-gpu") 
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage") 
    options.add_argument("--window-size=1920,1080") 
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) 
 
def check_availability(): 
    driver = setup_driver() 
    try: 
        driver.get(PARKSTAY_URL) 
        time.sleep(8) 
        html = driver.page_source.lower() 
 
        if any(k in html for k in ["book now", "add to cart", "available"]): 
            print(f"[{datetime.now()}]  Campsite appears available!") 
            send_email_notification() 
        else: 
            print(f"[{datetime.now()}]  No availability yet.") 
    except Exception as e: 
        print(f"[{datetime.now()}]  Error checking site: {e}") 
    finally: 
        driver.quit() 
 
def send_email_notification(): 
    subject = " Parks WA Campsite Available!" 
    body = f"A campsite may now be available! Check here:\n\n{PARKSTAY_URL}" 
 
    msg = MIMEMultipart() 
    msg["From"] = EMAIL_FROM 
    msg["To"] = EMAIL_TO 
    msg["Subject"] = subject 
    msg.attach(MIMEText(body, "plain")) 
 
    try: 
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server: 
            server.starttls() 
            server.login(EMAIL_FROM, EMAIL_PASSWORD) 
            server.send_message(msg) 
        print(f"[{datetime.now()}]  Email sent to {EMAIL_TO}") 
    except Exception as e: 
        print(f"[{datetime.now()}]  Failed to send email: {e}") 
 
def main(): 
    print(f"Monitoring: {PARKSTAY_URL}") 
    check_availability() 
 
if __name__ == "__main__": 
    print("Sending test email...")
 send_email_notification()
