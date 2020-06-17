from ai import Model
import jieba
import pickle
import json
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer


class BowModel(Model):
	def __init__(self):
		self.vectorizer = pickle.load(open('./vectorizer.pkl', 'rb'))
		self.classifier = pickle.load(open('./classifier.pkl', 'rb'))
		jieba.set_dictionary('./dict.txt.big.txt')

	def predict_text(self, text):
		tokenized_text = [' '.join(jieba.cut(text, cut_all=True))]

		vectorized_text = self.vectorizer.fit_transform(tokenized_text)

		return self.classifier.predict(vectorized_text)
