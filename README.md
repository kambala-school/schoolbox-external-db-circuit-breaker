# schoolbox-external-db-circuit-breaker
Check HTTP response time of Schoolbox and disable External DB connection after a specified threshold

Environment variables to be configured:
```shell
# How long to wait for a HTTP response before it disables the External DB
HTTP_TIMEOUT: 5
# How often it checks
CHECK_FREQUENCY: 30
# Email notifications
EMAIL_ENABLED: 1
# Server the app is running on. eg. schoolbox-prod
APP_HOST = 'schoolbox'
# URL to check performance of
HTTP_URL = 'https://schoolbox.com.au/pings'
# Schoolbox API token to authenticate to URL endpoint
HTTP_TOKEN = 'schoolboxAPItoken'
# Schoolbox Database Connection
MYSQL_HOST = 'schoolboxMySQLserver'
MYSQL_USER = 'user'
MYSQL_PASSWORD = 'password'
MYSQL_DB = 'schoolboxDB'
# Sendgrid API for email notifications
SENDGRID_API_KEY = 'apiKey'
EMAIL_FROM = 'from@email.com'
EMAIL_TO = 'to@email.com'
```