import os 
import me 
import smtplib 
from dateme import dateme 
from email.mime.text import MIMEText 
from email.mime.mul part import MIMEMul part 
from selenium import webdriver 
from selenium.webdriver.chrome.op ons import Op ons 
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome import ChromeDriverManager 
 
# ========================================================= 
#  CONFIGURATION — change these values if running locally 
# (GitHub Ac ons will override them using secrets) 
# ========================================================= 
 
SITE_ID = int(os.getenv("SITE_ID", 139))              # Campground/site ID 
ARRIVAL_DATE = os.getenv("ARRIVAL_DATE", "2025/11/07") 
DEPARTURE_DATE = os.getenv("DEPARTURE_DATE", "2025/11/08") 
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
    op ons = Op ons() 
    op ons.add_argument("--headless=new") 
    op ons.add_argument("--disable-gpu") 
    op ons.add_argument("--no-sandbox") 
    op ons.add_argument("--disable-dev-shm-usage") 
    op ons.add_argument("--window-size=1920,1080") 
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), op ons=op ons) 
 
def check_availability(): 
    driver = setup_driver() 
    try: 
        driver.get(PARKSTAY_URL) 
        me.sleep(8) 
        html = driver.page_source.lower() 
 
        if any(k in html for k in ["book now", "add to cart", "available"]): 
            print(f"[{dateme.now()}]  Campsite appears available!") 
            send_email_no fica on() 
        else: 
            print(f"[{dateme.now()}]  No availability yet.") 
    except Excep on as e: 
        print(f"[{dateme.now()}]  Error checking site: {e}") 
    finally: 
        driver.quit() 
 
def send_email_no fica on(): 
    subject = " Parks WA Campsite Available!" 
    body = f"A campsite may now be available! Check here:\n\n{PARKSTAY_URL}" 
 
    msg = MIMEMul part() 
    msg["From"] = EMAIL_FROM 
    msg["To"] = EMAIL_TO 
    msg["Subject"] = subject 
    msg.a ach(MIMEText(body, "plain")) 
 
    try: 
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server: 
            server.star ls() 
            server.login(EMAIL_FROM, EMAIL_PASSWORD) 
            server.send_message(msg) 
        print(f"[{dateme.now()}]  Email sent to {EMAIL_TO}") 
    except Excep on as e: 
        print(f"[{dateme.now()}]  Failed to send email: {e}") 
 
def main(): 
    print(f"Monitoring: {PARKSTAY_URL}") 
    check_availability() 
 
if __name__ == "__main__": 
    main()
