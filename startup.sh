service nginx start
cd /home/
uwsgi -s /tmp/flaskapp.sock --manage-script-name --mount /=flaskapp:app --chmod-socket=777
