# schoolbox-external-db-circuit-breaker
Check HTTP response time of Schoolbox and disable External DB connection after a specified threshold

### Installation
Create a user on the Schoolbox MySQL database with required permissions to the config table:
```shell
CREATE USER 'custom-user'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT, UPDATE ON schoolbox.config TO 'custom-user'@'localhost';
FLUSH PRIVILEGES;
```

Clone this repository and configure the following environment variables in a .env file:
```shell
# How long to wait for a HTTP timeout in seconds
HTTP_TIMEOUT = '5'
# How many timeouts to occur before it disables the External DB
MAX_TIMEOUTS = '3'
# How often it checks
CHECK_FREQUENCY = '30'
# Email notifications
EMAIL_ENABLED = '1'
# Debug mode to show HTTP response times
DEBUG_ENABLED = '0'
# Server the app is running on. eg. schoolbox-prod
APP_HOST = 'schoolbox'
# Domain name the app is hosted on
DOMAIN = 'domain.com.au'
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
# Timezone
TZ = 'Australia/Sydney'
```

Build and run the container locally or use docker-compose:
```shell
docker-compose pull
docker-compose up -d
```