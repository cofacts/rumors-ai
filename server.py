from flask import Flask, request
from data_manager import DataManager
from ai import ModelManager
import redis
import json
import schedule
import time
import settings
from pymongo import MongoClient

app = Flask(__name__)

mongodb_url = settings.MONGODB_ADDRESS

client = MongoClient(
    'mongodb://rumors:rumors1234@ds363088.mlab.com:63088/rumors-ai', 63088)
db_client = client['rumors-ai']
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
    return db_client.models.find()

# POST /v1/models/


@app.route('/v1/models', methods=['POST'])
def post_model():
    return db_client.models.insert_one(json.loads(request.get_json()))

# POST /v1/categorize/


'''
input:
{
    "content": "sample",
    "useModels": [ "mid-A", "mid-B", "mid-C" ],
    "source": "LINE",
    "callback": "https://myapp.io/callback",
    "metedata": {},
}
'''


@app.route('/v1/categorize', methods=['POST'])
def post_category():

    content = request.json['content']
    models = request.json['useModels']
    source = request.json['source']
    callback = request.json['callback']

    result = {
        'result': {
            'useModels': {

            }
        }
    }

    for model_id in models:
        local_model = model_manager.get_model(model_id)
        if local_model is None:

            db_client.tasks.insert_one({
                'modelId': model_id,
                'content': content,
                'source': source,
                'callback': callback
            })

            result['result']['useModels'][model_id] = {
                'pending': True
            }
        else:
            result['result']['useModels'][model_id] = local_model.predict_text(
                content)

    return result

# GET /v1/keyword/


@app.route('/v1/keyword/<date_string>', methods=['GET'])
def get_keyword(date_string):
    keyword_stats = db_client.keyword_stats.find_one({'date': date_string})

    return {
        'date': keyword_stats['date'],
        '1d': json.loads(keyword_stats['1d']),
        '3d': json.loads(keyword_stats['3d']),
        '7d': json.loads(keyword_stats['7d']),
        '30d': json.loads(keyword_stats['30d']),
    }

# GET /v1/tasks/${modelId}


@ app.route('/v1/tasks/<model_id>', methods=['GET'])
def get_tasks_by_model(model_id):
    return db_client.tasks.find({'modelId': model_id})

# POST /v1/tasks/${taskId}


@ app.route('/v1/tasks/<task_id>', methods=['POST'])
def finish_task(task_id):

    task = db_client.tasks.find_one({'id': task_id})

    callback_url = task['callback']

    db_client.tasks.delete_one({'id': task_id})

    # TODO: send result to callback endpoint
    # request.post(callback_url, request.body)

    return
