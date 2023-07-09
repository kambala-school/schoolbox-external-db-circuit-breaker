FROM python:3.9.17-slim-bullseye
RUN pip install requests mysql-connector-python python-dotenv sendgrid
COPY app .
CMD ["python", "-u", "./app.py"]