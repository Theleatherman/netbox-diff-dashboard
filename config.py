import os
from dotenv import load_dotenv

load_dotenv()

NETBOX_API_URL = os.getenv("NETBOX_API_URL")
NETBOX_API_TOKEN = os.getenv("NETBOX_API_TOKEN")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
DB_PATH = os.getenv("DB_PATH", "netbox.db")
