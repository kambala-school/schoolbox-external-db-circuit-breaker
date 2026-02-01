# syntax=docker/dockerfile:1
FROM python:3.13.5-slim-bullseye
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    python3-dev \
    && pip install requests mysql-connector-python python-dotenv sendgrid \
    && apt-get purge -y gcc libffi-dev python3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
COPY app .
CMD ["python", "-u", "./app.py"]
