FROM ubuntu:xenial

RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    nginx

RUN pip3 install flask
RUN pip3 install flask-restplus
RUN pip3 install uwsgi
RUN pip3 install psycopg2-binary
RUN pip3 install flask-sqlalchemy
RUN pip3 install flask-migrate
RUN pip3 install flask-wtf
RUN pip3 install itsdangerous
RUN pip3 install flask-mail
RUN pip3 install flask-login

EXPOSE 80

VOLUME /var/log/flaskapp
VOLUME /home/user_files/flaskapp

COPY site.conf /etc/nginx/sites-available
RUN ln -s /etc/nginx/sites-available/site.conf /etc/nginx/sites-enabled

COPY startup.sh /home
RUN chmod 777 /home/startup.sh
CMD ["bash","/home/startup.sh"]

COPY flaskapp /home/