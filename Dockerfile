# syntax=docker/dockerfile:1
FROM python:3.14.0a3-slim-bullseye
RUN pip install requests mysql-connector-python python-dotenv sendgrid
COPY app .
CMD ["python", "-u", "./app.py"]
