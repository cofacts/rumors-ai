git clone https://github.com/cofacts/rumors-ai
mv rumors-ai rumors-ai-stg
git clone https://github.com/cofacts/rumors-ai
mv rumors-ai rumors-ai-prod
cd ~/rumors-ai-stg
FLASK_APP=server.py ENV=staging python3 -m flask run --port=5001
cd ~/rumors-ai-prod
FLASK_APP=server.py ENV=production python3 -m flask run --port=5001