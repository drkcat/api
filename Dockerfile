FROM python:alpine

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "gunicorn", "--workers", "3", "--bind", "unix:/var/run/app/api.sock", "api:__hug_wsgi__" ]