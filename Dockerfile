FROM python:3.13.0b1-slim-bullseye
RUN pip install requests mysql-connector-python python-dotenv sendgrid
COPY app .
CMD ["python", "-u", "./app.py"]