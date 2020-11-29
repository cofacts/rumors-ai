
from data_manager import DataManager
from ai import ModelManager
import datetime
from jobs import keyword_analysis
import pickle

data_manager = DataManager()

data_manager.sync_out()

keyword_analysis(data_manager)
