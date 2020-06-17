# from ai import Model
import jieba
import pickle
import json
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer


class BowModel:
	def __init__(self):
		self.vectorizer = pickle.load(open('./ai/models/bow/vectorizer.pkl', 'rb'))
		self.classifier = pickle.load(open('./ai/models/bow/classifier.pkl', 'rb'))
		jieba.set_dictionary('./ai/models/bow/dict.txt.big.txt')

	def predict_text(self, text):
		tokenized_text = [' '.join(jieba.cut(text, cut_all=True))]

		vectorized_text = self.vectorizer.transform(tokenized_text)

		return list(map(int, self.classifier.predict(vectorized_text)))
