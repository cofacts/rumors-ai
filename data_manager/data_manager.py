from gql import gql, Client
from graphql import build_ast_schema, parse
import os
import datetime
import pickle

from gql.transport.requests import RequestsHTTPTransport

COFACTS_GRAPHQL_SERVER = 'https://cofacts-api.g0v.tw/graphql'

class DataManager:
  def __init__(self):
    transport=RequestsHTTPTransport(
      url=COFACTS_GRAPHQL_SERVER,
      use_json=True,
      headers={
          "Content-type": "application/json",
      },
      verify=False
    )

    schema = build_ast_schema(parse(open('schema.graphql').read()))

    self.client = Client(schema=schema, transport=transport)

    article_list_files = sorted(os.listdir('./data/article_list'))

    latest_article_list_filename = None if len(article_list_files) == 0 else article_list_files[-1]

    self.last_updated = latest_article_list_filename[:-4]

    self.article_list = pickle.load(open('./data/article_list/{}'.format(latest_article_list_filename), 'rb'))

    article_files = os.listdir('./data/articles')

    self.articles = {}

    print(article_files)

    for article_file in article_files:
      article = pickle.load(open('./data/articles/{}'.format(article_file), 'rb'))
      self.articles[article['id']] = article

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
    pickle.dump(self.article_list, open('./data/article_list/{}.pkl'.format(current_date_string), 'wb'))

  def update_articles(self):
    for article_id in self.article_list:
      if article_id not in self.articles:
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

        pickle.dump(result, open('./data/articles/{}.pkl'.format(article_id), 'wb'))

  def sync_in(self):
    self.update_article_list()
    self.update_articles()

  def sync_out(self):

    query_string = '''
      {{
        UpdateArticleTags(
          id: "{}"
        )
      }}
    '''.format()
