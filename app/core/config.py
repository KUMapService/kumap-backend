import os

from dotenv import load_dotenv

load_dotenv()

APP_DIR = os.getenv("APP_DIR")
BASE_DIR = os.getenv("BASE_DIR")

# DATABASE
ROOT_PW = os.getenv("ROOT_PW")
DATABASE_NAME = os.getenv("DATABASE_NAME")
USER_NAME = os.getenv("USER_NAME")
USER_PW = os.getenv("USER_PW")

# API KEY
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
KAKAO_JAVASCRIPT_API_KEY = os.getenv("KAKAO_JAVASCRIPT_API_KEY")
VWORLD_API_KEY = os.getenv("VWORLD_API_KEY")
LAND_API_KEY = os.getenv("LAND_API_KEY")
ECOS_API_KEY = os.getenv("ECOS_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# MAIL
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# PREDICTION MODEL
MODEL_PATH = os.getenv("MODEL_PATH")
LLM_MODEL = os.getenv("LLM_MODEL")

# SERVER CONFIGURATION
SERVER_PORT = int(os.getenv("SERVER_PORT"))
SERVER_DOMAIN = os.getenv("SERVER_DOMAIN")

# JWT CONFIG
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
