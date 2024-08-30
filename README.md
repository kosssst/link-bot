# Link-bot

Sends link for online lessons on pre-determined time.

Characteristics:
- different schedule for 1st and 2nd week;
- 6-days week;
- up to 5 lessons in a day;
- ability to manually set time of each lesson;

## How to build and run:

1. ### Fill `config.py`:
In folder `configs/` there is template for `config.py`. You should fill it with your data.

2. ### Fill `.env`:
**Important:** You should fill it like `.env_template`. Without it bot wont work.

3. ### Build docker image:
```shell
docker build -t kosssst_link_bot:latest .
```

4. ### Start docker container:
```shell
docker compose up -d
```