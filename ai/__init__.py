from data_manager import DataManager
from ai.models.bow import BowModel
# from preprocess import 

class Model:
	def __init__(self):
		pass

	def predict(self, text):
		raise Exception('not implemented')

class ModelManager:
	DEFAULT_CONFIG = [
		{
			'name': 'bert'
		},
		{
			'name': 'bow'
		}
	]

	def __init__(self, config=DEFAULT_CONFIG):
		self.config = config
		self.prediction_result = {}
		self.models = {}
	
	def get_model(self, model_name):
		try:
			if model_name == 'bow':
				if model_name not in self.models:
					self.models[model_name] = BowModel()
				return self.models[model_name]
		except:
			print('Model named {} not found.'.format(model_name))
		
		return None
		

	def predict_all(self):
		article_list_files = sorted(os.listdir('../../../data/article_list'))

		latest_article_list_filename = None if len(article_list_files) == 0 else article_list_files[-1]

		last_updated = latest_article_list_filename[:-4]

		article_list = pickle.load(open('../../../data/article_list/{}'.format(latest_article_list_filename), 'rb'))

		text = pickle.load(open('../../../data/articles/{}.pkl'.format(article_id), 'rb'))['text']
        
		articles_text = []

		for article_id in article_list:
			text = pickle.load(open('../../../data/articles/{}.pkl'.format(article_id), 'rb'))['text']
			articles_text.append(text)

		for model in self.config:
			self.get_model(model['name']).predict(articles_text)


	def write_result(self):
		
		for model in self.config:
			result[model['name']] = {}

			for i, article_id in enumerate(article_list):
				results['bert'][article_id] = [(staging_predicts[i], 1.0)]

		pickle.dump(results, open('../../../result/20200507.pkl', 'wb'))
		pass
