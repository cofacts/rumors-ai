# rumors-ai
Article categorizer for cofacts.

## Repo structures
    .
    ├── data                          # Store untagged articles
    ├── data_exploration              # Flow labeled data exploration results
    ├── data_manager                  # Data manager for synchronizing articles
    ├── ai_model                      # ML model pipelines
    │     ├── data                    # Data for traning ML models
    │     │     ├── raw_data          # Labeled raw data (by Flow or Cofacts)
    │     │     └── processed_data    # Data after preprocessing (feed to ML models)
    │     ├── preprocess              # Preprocess programs
    │     ├── models                  # ML models
    │     │     ├── model_A           # ML model developed by gary9630
    │     │     └── model_B           # ML model developed by darkbtf
    │     └── eval                    # Model evaluation programs for fair comparison
    ├── result                        # Store tagged articles
    └── .env                          # Environment variables (see ## Configuration)


## Install
This project uses python 3.7 and docker (docker-compose).

Make sure you have these up-to-date.

For example, here's prerequisite installation for ubuntu.
```
apt update
apt install python3
apt install docker.io
apt install docker-compose
```


Install python dependencies:
```
pip3 install -r requirements.txt
```

## Run
1. use `docker-compose` to startup all services.
```
docker-compose up -d
```
2. run the main flask app
```
FLASK_APP=server.py flask run
```

## Deployment
This project has been tested on GCP n1-standard VM
* 1 CPU
* 3.75G RAM
* 80G Standard Disk
* Ubuntu 16.04 LTS
<img src="https://i.imgur.com/ltTcT0K.png" width="720" />
<img src="https://i.imgur.com/PKvQcEm.png" width="720" />

## Usage
* Go to the index (http://localhost:5000 on your local) and see the current job queue. (Currently only data syncing)
<img src="https://i.imgur.com/4usppvU.png" width="720" />

* This server synchronizes article list and articles on daily basis under these paths:
  * article list: `data/article_list/<date>.pkl`
  * articles: `data/articles/<article_id>.pkl`.
<img src="https://i.imgur.com/ERoYmoP.png" width="720" />

## Notes
### Artlcle Format
<TODO>

### Result Format
```
{
  [model_name]: {
    [article_id]: [
      (category_id, confidence)
    ]
  }
}
```

## Environment Variables
see [.env.example](.env.example)

| Environment Variable | Description |
| -------- | -------- |
| ENV     | environment. default: `development` |
| INSTANCE_NAME     | Instance name used for logging. default: `development`     |
| REDIS_HOST     | host of Redis. default: `localhost`     |
| REDIS_PORT     | port of Redis. default: `6379`     |
| MONGODB_ADDRESS     | address of MongoDB. default: `localhost`     |
| MONGODB_PORT     | port of MongoDB. default: `27017`     |
| MONGODB_NAME     | name of MongoDB database . default: `rumors-ai`     |

