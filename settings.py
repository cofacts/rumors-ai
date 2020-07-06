from dotenv import load_dotenv
import os

load_dotenv()

ENV = os.getenv('ENV')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
MONGODB_ADDRESS = os.getenv('MONGODB_ADDRESS')
MONGODB_PORT = os.getenv('MONGODB_PORT')
MONGODB_NAME = os.getenv('MONGODB_NAME')