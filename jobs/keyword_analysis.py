import jieba.analyse
import json
import settings
from pymongo import MongoClient
from datetime import datetime, timedelta


client = MongoClient(settings.MONGODB_ADDRESS, int(settings.MONGODB_PORT))
db_client = client['rumors-ai']

MAX_KEYWORD_COUNT = 100
TIME_WINDOWS = [1, 3, 7, 30]

def keyword_analysis(data_manager):
    latest_date = datetime.strptime(list(db_client.keyword_stats.find().sort([('date', -1)]).limit(1))[0]['date'], '%Y%m%d').date()
    
    date_i = latest_date + timedelta(days=1)
    current_date = datetime.today().date()

    # last_interested_date = latest_date - timedelta(days=max(max(TIME_WINDOWS)-1,0))

    # build date dictionary
    article_date_dict = {}

    for article in data_manager.articles.values():
        if article['createdAt'] is not None:
            article_date_string = datetime.strptime(article['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y%m%d')
            if article_date_string not in article_date_dict:
                article_date_dict[article_date_string] = []
            article_date_dict[article_date_string].append(article['text'])


    while date_i <= current_date:

        keyword_stat = {
            'date': date_i.strftime('%Y%m%d')
        }

        for time_window in TIME_WINDOWS:
            date_j = date_i
            article_bucket = []
            for _ in range(time_window):
                date_string = date_j.strftime('%Y%m%d')
                if date_string in article_date_dict:
                    article_bucket.extend(article_date_dict[date_string])
                date_j -= timedelta(days=1)
            tags = jieba.analyse.extract_tags(' '.join(article_bucket), topK=MAX_KEYWORD_COUNT, withWeight=True)
            keyword_stat[str(time_window)+'d'] = json.dumps(dict(tags), ensure_ascii=False)

        print(keyword_stat)
    
        db_client.keyword_stats.insert_one(keyword_stat)

        date_i += timedelta(days=1)
