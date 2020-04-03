# rumors-ai
Article categorizer for cofacts.

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
