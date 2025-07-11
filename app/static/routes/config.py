import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "devkey")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://postgres:password@localhost/boathouse")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
