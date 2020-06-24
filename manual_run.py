
from data_manager import DataManager
from ai import ModelManager
import datetime

import pickle

data_manager = DataManager()
model_manager = ModelManager()

model = model_manager.get_model('bow')
# data_manager.sync_in()
# data_manager.sync_out()

# print(data_manager.articles)

filtered_articles = list(filter(lambda article: len(article['articleCategories']) == 0, data_manager.articles.values()))

print('filtered length', len(filtered_articles))

result = model.predict(filtered_articles)

result_mapping = {
    'bow': {}
}

for i, article in enumerate(filtered_articles):
    result_mapping['bow'][article['id']] = [(result[i], 1.0)]

print(result_mapping)

current_date_string = datetime.datetime.now().strftime('%Y%m%d')
pickle.dump(result_mapping, open('./result/staging/{}.pkl'.format(current_date_string), 'wb'))

data_manager.sync_out()

# import settings

# print(settings.REDIS_ADDRESS)