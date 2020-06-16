from flask import Flask, request
from data_manager import DataManager
from ai import ModelManager
import redis
import json
import schedule
import time
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

data_manager = DataManager()
model_manager = ModelManager()

def process_queue():
  global redis_client

  if redis_client.get('current') == None:
    job_list = redis_client.lrange('jobs', 0, -1)
    
    if len(job_list) > 0:
      current_job_str = redis_client.lpop('jobs')
      redis_client.set('current', current_job_str)
      job_strs = current_job_str.split('.')

      current_job = job_strs[0]
      parameters = [] if len(job_strs) <= 1 else job_strs[1:]

      if current_job == 'sync_in':
        data_manager.sync_in()
      elif current_job == 'sync_out':
        data_manager.sync_out()
      elif current_job == 'train':
        print('Online training not implemented, please train models manually')
      elif current_job == 'predict':
        model_name = parameters[0]
        model_manager.get_model(model_name).predict()
      else:
        print('Unknown job:', current_job)

      redis_client.delete('current')
        

def push_job(job_string):
  global redis_client

  def push_actual_job():
    job_list = redis_client.lrange('jobs', 0, -1)
    if job_string not in job_list:
      redis_client.lpush('jobs', job_string)

  return push_actual_job

schedule.every().minute.do(process_queue)
schedule.every().day.at('02:30').do(push_job('sync_in'))
schedule.every().day.at('02:45').do(push_job('predict.bert'))
schedule.every().day.at('03:00').do(push_job('sync_out'))

def get_status():
  return '''
    Current Job: {}
    Current Queue: {}
    Last Updated: {}
  '''.format(
    redis_client.get('current'),
    redis_client.lrange('jobs', 0, -1),
    data_manager.last_updated
  )

@app.route('/')
def index():
  return get_status()

@app.route('/sync_in')
def sync_in():
  data_manager.sync_in()

@app.route('/run_model')
def run_model():
  push_job('predict.bert')

  return get_status()

# GET /v1/models/
@app.route('/v1/models', methods=['GET'])
def get_model():
  return client.models.find()

# POST /v1/models/
@app.route('/v1/models', methods=['POST'])
def post_model():
  return client.models.insert_one(json.loads(request.get_json()))

# POST /v1/categorize/
@app.route('/v1/categorize', methods=['POST'])
def post_category():
  return {
    "id": "this-is-mongo-object-id",
    "name": "my ai model",
    "apiKey": "zzzzzz",
    "createdAt": "2020-06-03"
  }

# GET /v1/keyword/
@app.route('/v1/keyword/', methods=['POST'])
def get_keyword():
  return {
    "id": "this-is-mongo-object-id",
    "name": "my ai model",
    "apiKey": "zzzzzz",
    "createdAt": "2020-06-03"
  }
