# schoolbox-external-db-circuit-breaker
Monitor HTTP response time and status codes of Schoolbox and disable External DB connection after a specified threshold of failures

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
# How many failures (timeouts or HTTP error status codes) to occur before it disables the External DB
MAX_TIMEOUTS = '3'
# How often it checks
CHECK_FREQUENCY = '30'
# Email notifications
EMAIL_ENABLED = '1'
# Debug mode to show HTTP response times and status codes
DEBUG_ENABLED = '0'
# Server the app is running on. eg. schoolbox-prod
APP_HOST = 'schoolbox'
# Domain name the app is hosted on
DOMAIN = 'domain.com.au'
# URL to check performance of
HTTP_URL = 'https://schoolbox.com.au/ping'
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

### How It Works

The circuit breaker monitors the HTTP endpoint specified in `HTTP_URL` at regular intervals (`CHECK_FREQUENCY`). The circuit breaker will trigger and disable the External DB connection when:

1. **HTTP Timeouts**: The request exceeds `HTTP_TIMEOUT` seconds
2. **HTTP Error Status Codes**: The server returns any status code other than 200 (e.g., 302 redirects, 401 authentication failures, 403 forbidden, 404 not found, 500+ server errors)

The circuit breaker uses a retry mechanism: it will attempt up to `MAX_TIMEOUTS` times before disabling the External DB. Each failure (timeout or non-200 status code) increments the attempt counter. If a successful response (HTTP 200) is received, the attempt counter is reset.

**Note**: Redirects are not automatically followed (`allow_redirects=False`) to detect authentication failures that may result in redirect responses.

Build and run the container locally or use docker-compose:
```shell
docker-compose pull
docker-compose up -d
```