import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT", 1234))
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SETTINGS_FILE = os.environ.get("SETTINGS_FILE")
