import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "********")

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER", "images/temp/")

DB_PATH = os.getenv("DB_PATH", "data/receipts.db")

OWNER_USERNAME = "EyuSim"