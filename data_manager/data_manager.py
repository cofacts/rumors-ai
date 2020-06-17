from gql import gql, Client
from graphql import build_ast_schema, parse
import os
import datetime
import pickle
import traceback
import time

from gql.transport.requests import RequestsHTTPTransport

COFACTS_GRAPHQL_SERVER = {
  'staging': 'https://cofacts-api.hacktabl.org/graphql',
  'production': 'https://cofacts-api.g0v.tw/graphql'
}
ENV = 'production'

CATEGORY_ID_MAPPING = [
  'kj287XEBrIRcahlYvQoS', # 0 中國影響力
  'kz3c7XEBrIRcahlYxAp6', # 1 性少數與愛滋病
  'lD3h7XEBrIRcahlYeQqS', # 2 女權與性別刻板印象
  'lT3h7XEBrIRcahlYugqq', # 3 保健秘訣、食品安全
  'lj2m7nEBrIRcahlY6Ao_', # 4 基本人權問題
  'lz2n7nEBrIRcahlYDgri', # 5 農林漁牧政策
  'mD2n7nEBrIRcahlYLAr7', # 6 能源轉型
  'mT2n7nEBrIRcahlYTArI', # 7 環境生態保護
  'mj2n7nEBrIRcahlYdArf', # 8 優惠措施、新法規、政策宣導
  'mz2n7nEBrIRcahlYnQpz', # 9 科技、資安、隱私
  'nD2n7nEBrIRcahlYwQoW', # 10 免費訊息詐騙
  'nT2n7nEBrIRcahlY6QqF', # 11有意義但不包含在以上標籤
  'nj2n7nEBrIRcahlY-gpc', # 12 無意義
  'nz2o7nEBrIRcahlYBgqQ', # 13 廣告
  'oD2o7nEBrIRcahlYFgpm', # 14 只有網址其他資訊不足
  'oT2o7nEBrIRcahlYKQoM', # 15 政治、政黨
  'oj2o7nEBrIRcahlYRAox' # 16 轉發協尋、捐款捐贈
]

class DataManager:
  def __init__(self):
    transport=RequestsHTTPTransport(
      url=COFACTS_GRAPHQL_SERVER[ENV]+'?userId=bert',
      use_json=True,
      headers={
          "Content-type": "application/json",
          "x-app-secret": "rumors-ai"
      },
      verify=False
    )

    schema = build_ast_schema(parse(open('schema.graphql').read()))

    self.client = Client(schema=schema, transport=transport)

    article_list_files = sorted(os.listdir('./data/{}/article_list'.format(ENV)))

    if len(article_list_files) > 0:
      latest_article_list_filename = article_list_files[-1]

      self.last_updated = latest_article_list_filename[:-4]

      self.article_list = pickle.load(open('./data/{}/article_list/{}'.format(ENV, latest_article_list_filename), 'rb'))

      article_files = os.listdir('./data/{}/articles'.format(ENV))

    self.articles = {}

    # for article_file in article_files:
    #   article = pickle.load(open('./data/{}/articles/{}'.format(ENV, article_file), 'rb'))
    #   self.articles[article['id']] = article

    self.models = {}

  def update_article_list(self):
    cursor = ''

    self.article_list = []

    while True:

      query_string = '''
        {{
          ListArticles(
            orderBy: [{{ _score: DESC }}]
            first: 2000
            after: "{}"
          ) {{
              totalCount
              edges {{
                cursor
                node {{
                  id
                }}
              }}
          }}
        }}
      '''.format(cursor)

      query = gql(query_string)

      result = self.client.execute(query)

      edges = result['ListArticles']['edges']

      if len(edges) == 0: break

      for edge in edges:
        self.article_list.append(edge['node']['id'])

      cursor = edges[-1]['cursor']

    current_date_string = datetime.datetime.now().strftime('%Y%m%d')
    pickle.dump(self.article_list, open('./data/{}/article_list/{}.pkl'.format(ENV, current_date_string), 'wb'))

  def update_articles(self):
    print('fuck')
    for i, article_id in enumerate(self.article_list):
      if article_id not in self.articles:
        print(i)
        query_string = '''
          {{
            GetArticle(
              id: "{}"
            ) {{
              id
              text
              createdAt
              references {{
                type
              }}
              articleCategories {{
                category {{
                  id
                  title
                }}
              }}
              hyperlinks {{
                url
                title
                summary
              }}
            }}
          }}
        '''.format(article_id)

        query = gql(query_string)

        result = self.client.execute(query)['GetArticle']

        self.articles[article_id] = result

        pickle.dump(result, open('./data/{}/articles/{}.pkl'.format(ENV, article_id), 'wb'))

  def sync_in(self):
    self.update_article_list()
    self.update_articles()

  def write_labels(self):
    files = list(os.listdir('./result/{}'.format(ENV)))

    latest_result = sorted(files, reverse=True)[0]

    results = pickle.load(open('./result/{}/{}'.format(ENV, latest_result), 'rb'))
    
    for model_name in results.keys():
      model_result = results[model_name]
      # TODO: change model_name in gql request

      for article_id in model_result.keys():
        
        article = pickle.load(open('./data/{}/articles/{}.pkl'.format(ENV, article_id), 'rb'))
        
        categories = list(map(lambda element: element['category']['id'], article['articleCategories']))

        labels = model_result[article_id]

        for label in labels:
          if CATEGORY_ID_MAPPING[label[0]] not in categories:
            query_string = '''
              mutation {{
                CreateArticleCategory(
                  articleId: "{}"
                  categoryId: "{}"
                  aiModel: "{}"
                  aiConfidence: {}
                ) {{
                  articleId
                  categoryId
                }}
              }}
            '''.format(article_id, CATEGORY_ID_MAPPING[label[0]], model_name, label[1])

            query = gql(query_string)
            # self.client.execute(query)

            time.sleep(10)

            try:
              self.client.execute(query)
            except Exception:
              print(traceback.format_exc())
              print(query_string)
    
    return

  def sync_out(self):
    self.write_labels()

