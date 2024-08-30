FROM python:3.9.18-slim-bullseye

WORKDIR /link-bot

COPY main.py /link-bot/
COPY requirements.txt /link-bot/

RUN mkdir /link-bot/configs

RUN pip install -r requirements.txt

CMD ["python", "main.py"]