# Purpose

Flask application which is:
* a simple API with restricted access to premium users only
* JWT authentication
* a Swagger documentation
* a user web interface for registration with email activation, lost password recovery, and token retrieval

# Dev

Development is done by launching Flask local web server: `FLASK_APP=flaskapp.py flask run`

# Prod

The application is deployed with Docker. The front web server is Nginx. The connector between Flask and Nginx is uwsgi.

Here is the command in order to create and launch a Docker container in production.

```
docker run \ 
--publish 80:80 \
--volume /var/log/flaskapp:var/log/flaskapp \
--volume /home/user_files/flaskapp:/home/user_files/flaskapp \
--env "USER_FOLDERS_PATH=/home/user_files/flaskapp" \
--env "LOG_FILE_PATH=/var/log/flaskapp" \
--detach \
--name my_container \
my_acoount/my_repo:my_tag
```

# Database migrations

Run local migrations during dev:
1. `FLASK_APP=flaskapp.py flask db init (first time only)`
1. `FLASK_APP=flaskapp.py flask db migrate`
1. `FLASK_APP=flaskapp.py flask db upgrade`

Once the app is ready to go to production, change database credentials in order to connect to production database and create tables structure:
* `FLASK_APP=flaskapp.py flask upgrade`
