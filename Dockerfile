FROM python:3.9.16-alpine3.17

COPY . /opt/app/
WORKDIR /opt/app

RUN python3 -m pip install -r requirements.txt

CMD python3 main.py