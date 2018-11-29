FROM tiangolo/uwsgi-nginx:python3.7
LABEL maintainer="rr-"

ENV LISTEN_PORT 80
ENV UWSGI_INI /app/uwsgi.ini

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./app/nginx.conf /etc/nginx/conf.d/nginx.conf

COPY ./app /app
WORKDIR /app

COPY /app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
