# schoolbox-external-db-circuit-breaker
Check HTTP response time of Schoolbox and disable External DB connection after a specified threshold

Environment variables to be configured:
```
HTTP_TIMEOUT: 5
CHECK_FREQUENCY: 30
EMAIL_ENABLED: 1
APP_HOST = schoolbox
HTTP_URL = 'https://schoolbox.com.au/pings'
HTTP_TOKEN = 'httpToken'
MYSQL_HOST = 'mysql'
MYSQL_USER = 'user'
MYSQL_PASSWORD = 'password'
MYSQL_DB = 'db'
SENDGRID_API_KEY = 'apiKey'
EMAIL_FROM = 'from@email.com'
EMAIL_TO = 'to@email.com'
```