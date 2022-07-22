# Foodgram
![foodgram_workflow.yml](https://github.com/serjb1973/foodgram-project-react/actions/workflows/main.yml/badge.svg)
## project creation and processing of 
## culinary recipes and free exchange of them
##### _-Install and run services in docker-compose environment_
```git clone ...```
```cd foodgram-project-react/infra```
```touch .env```
> For example: .env
```sh
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
```sudo docker-compose up -d --build```
##### _-Install requirements and load initial_
```
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py collectstatic --no-input
sudo docker-compose exec backend python manage.py load_all_data
sudo docker-compose exec backend python manage.py createsuperuser
```
##### _-Admin connection for initial load dictionaries_
#
```sh
http://<You address>/admin/
```
##### _-Normal connection for work_
#
```sh
http://<You address>
```
> For example:
```sh
login/pass=serjb73@yandex.ru/admin
http://51.250.99.180/admin/
login/pass=tester1@tester1.ru/tester1
http://51.250.99.180/
```
## Authors
idea - https://practicum.yandex.ru
frondend - https://practicum.yandex.ru
backend - _Sergey Birukov_
