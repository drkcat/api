FROM python:alpine

RUN pip3 install -r requirements.txt

COPY . /app

WORKDIR /app

CMD [ "gunicorn", "--workers", "3", "--bind", "unix:/var/run/app/api.sock", "api:__hug_wsgi__" ]