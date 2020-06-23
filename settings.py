from dotenv import load_dotenv
import os

load_dotenv()

ENV = os.getenv('ENV')
REDIS_ADDRESS = os.getenv('REDIS_ADDRESS')
MONGODB_ADDRESS = os.getenv('MONGODB_ADDRESS')
