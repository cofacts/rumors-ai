from flask import Flask
from data_manager import DataManager
import redis
import schedule
import time

app = Flask(__name__)

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

data_manager = DataManager()

@app.route('/')
def index():

  return '''
    Current Job: {}
    Current Queue: {}
    Last Updated: {}
  '''.format(
    redis_client.get('current'),
    redis_client.lrange('jobs', 0, -1),
    data_manager.last_updated
  )

@app.route('/sync_in')
def sync_in():
  data_manager.sync_in()

@app.route('/run_model')
def run_model():
  pass

