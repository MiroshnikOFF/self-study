python3 -m venv env
source env/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic --no-input
deactivate

docker-compose down
docker-compose up --build -d
