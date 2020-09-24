from flask import Flask, request, jsonify
from data_manager import DataManager
from ai import ModelManager
import redis
import json
import schedule
import time
import settings
import threading
from jobs import keyword_analysis
from pymongo import MongoClient
from secrets import token_urlsafe
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient(
    settings.MONGODB_ADDRESS, int(settings.MONGODB_PORT))

db_client = client[settings.MONGODB_NAME]
redis_client = redis.Redis(host=settings.REDIS_HOST,
                           port=settings.REDIS_PORT, decode_responses=True)

data_manager = DataManager()
model_manager = ModelManager()


def remove_object_id(object):
    object['id'] = str(object['_id'])
    object.pop('_id', None)
    return object


def process_queue():
    global redis_client

    print('process lah')

    if redis_client.get('current') == None:
        job_list = redis_client.lrange('jobs', 0, -1)

        if len(job_list) > 0:
            current_job_str = redis_client.lpop('jobs')
            redis_client.set('current', current_job_str)

            db_client.jobs.insert_one({
                'instance': settings.INSTANCE_NAME,
                'job': current_job_str
            })

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
            elif current_job == 'keyword':
                keyword_analysis(data_manager)
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
schedule.every().day.at('02:45').do(push_job('keyword'))
schedule.every().day.at('03:00').do(push_job('predict.bow'))
schedule.every().day.at('03:30').do(push_job('sync_out'))

cease_continuous_run = threading.Event()


class ScheduleThread(threading.Thread):
    @classmethod
    def run(cls):
        while not cease_continuous_run.is_set():
            schedule.run_pending()
            time.sleep(5)


continuous_thread = ScheduleThread()
continuous_thread.start()


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
    push_job('predict.bow')

    return get_status()

# GET /v1/models/


@app.route('/v1/models', methods=['GET'])
def get_model():
    return {
        'result': list(map(remove_object_id, list(db_client.models.find())))
    }

# POST /v1/models/


@app.route('/v1/models', methods=['POST'])
def post_model():
    model_info = request.get_json()

    model_info['apiKey'] = token_urlsafe(32)
    model_info['approved'] = False

    db_client.models.insert_one(model_info)

    return remove_object_id(model_info)

# POST /v1/categorize/


'''
input:
{
    "content": "sample",
    "useModel": "mid-A", "mid-B", "mid-C",
    "source": "LINE",
    "callback": "https://myapp.io/callback",
    "metedata": {},
}
'''


@app.route('/v1/categorize', methods=['POST'])
def post_category():

    content = request.json.get('content')
    model = request.json.get('useModel')
    source = request.json.get('source')
    callback = request.json.get('callback')

    result = {}

    local_model = model_manager.get_model(model)
    if local_model is None:

        db_client.tasks.insert_one({
            'modelId': model,
            'content': content,
            'source': source,
            'callback': callback
        })

        result['result'] = {
            'pending': True
        }
    else:
        result['result'] = local_model.predict_text(content)

    return result

# GET /v1/keyword/


@app.route('/v1/keyword/<date_string>', methods=['GET'])
def get_keyword(date_string):
    keyword_stats = db_client.keyword_stats.find_one({'date': date_string})

    entry = {} if keyword_stats is None else {
        'date': keyword_stats['date'],
        '1d': json.loads(keyword_stats['1d']),
        '3d': json.loads(keyword_stats['3d']),
        '7d': json.loads(keyword_stats['7d']),
        '30d': json.loads(keyword_stats['30d']),
    }

    return entry

# GET /v1/tasks/${modelId}


@ app.route('/v1/tasks', methods=['GET'])
def get_tasks_by_model():
    model_id = request.args.get('modelId')
    criteria = {'modelId': model_id}
    if request.args.get('test') is None:
        criteria['result'] = {'$exists': False}
    return json.dumps(list(map(remove_object_id, list(db_client.tasks.find(criteria)))), indent=2, ensure_ascii=False)

# POST /v1/tasks/${taskId}


@ app.route('/v1/tasks', methods=['POST'])
def finish_task():

    res = []

    for task in request.json:
        if task['result'] is None:
            # TODO: empty result
            pass
        update_result = db_client.tasks.update_one({'_id': ObjectId(task['id'])}, {
                                                   '$set': {'result': task['result']}}, upsert=False)
        print(update_result)
        res.append({
            'id': task['id'],
            'result': {
                'ok': True
            }
        })

    # result = request.post(callback_url, data=json.loads(request.get_json()))

    # if result.status_code != 200:
    #     print('callback failed')

    return jsonify(res)
