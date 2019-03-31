FROM tiangolo/uwsgi-nginx:python3.6-alpine3.8

ENV NGINX_MAX_UPLOAD 1m
ENV LISTEN_PORT 8080

COPY . /app

WORKDIR /app
RUN pip3 install -r requirements.txt

EXPOSE 8080
