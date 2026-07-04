from pymongo import MongoClient
from flask_mail import Mail
from config import Config

_client = MongoClient(Config.MONGO_URI)
db = _client.get_default_database()

mail = Mail()
