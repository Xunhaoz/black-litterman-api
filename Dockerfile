FROM python:3.9


WORKDIR /app
COPY './requirements.txt' .

RUN apt-get update -y
RUN pip install -r requirements.txt

COPY . .
CMD exec gunicorn --bind :80 app:app
