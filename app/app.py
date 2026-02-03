import requests
import time
import os
import mysql.connector
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime
from dotenv import load_dotenv

# Parameters
load_dotenv()
check_frequency = int(os.getenv("CHECK_FREQUENCY"))
http_timeout = float(os.getenv("HTTP_TIMEOUT"))
max_timeouts = int(os.getenv("MAX_TIMEOUTS"))
current_attempts = 1
http_url = os.getenv("HTTP_URL")
http_token = os.getenv("HTTP_TOKEN")
http_headers = {
  "Authorization": f"Bearer {http_token}",
  "Accept": "application/json",
  "Content-Type": "application/json"
}

# Email settings
sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
from_email = Email(os.getenv('EMAIL_FROM')) 
to_email = To(os.getenv('EMAIL_TO')) 

# Print configuration at startup
print("http_url:", http_url)
print("check_frequency:", check_frequency)
print("http_timeout:", http_timeout)
print("max_timeouts:", max_timeouts)
print("from_email:", os.getenv('EMAIL_FROM'))
print("to_email:", os.getenv('EMAIL_TO'))
print("email_enabled:", os.getenv("EMAIL_ENABLED"))
print("debug_enabled:", os.getenv("DEBUG_ENABLED"))

def disable_external_db(reason="Unknown reason"):
    """
    Circuit breaker function that disables external_enable in the database.
    Handles database connection, update, and email notifications.
    
    Args:
        reason: A descriptive string explaining why the external DB is being disabled
    """
    timestamp = datetime.now()
    try:
        # Update MySQL database if response time is exceeded
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB")
        )
        cursor = connection.cursor()
        update_query = "UPDATE config SET value = 0 WHERE name = 'external_enable';"
        cursor.execute(update_query)
        connection.commit()
        cursor.close()
        connection.close()
        # Reset attempts
        global current_attempts
        current_attempts = 1

    except Exception as err:
        print(timestamp, "DATABASE ERROR", err)
        if(int(os.getenv("EMAIL_ENABLED"))):
            # Send email notification regarding FATAL event
            subject = os.getenv("APP_HOST") + "- FATAL Failed to disable External DB"
            body = f"""The schoolbox-external-db-circuit-breaker app failed to disable the External DB (Edumate).

Reason for attempted disable: {reason}
HTTP URL: {http_url}
HTTP timeout: {http_timeout}
Max attempts: {max_timeouts}
Current attempts: {current_attempts}

Database error: {str(err)}
"""
            content = Content("text/plain", body)
            mail = Mail(from_email, to_email, subject, content)
            mail_json = mail.get()
            response = sg.client.mail.send.post(request_body=mail_json)
        pass

    else:
        print(timestamp, "External DB has been disabled. Reason:", reason)
        if(int(os.getenv("EMAIL_ENABLED"))):
            # Send email notification regarding CRITICAL event
            subject = os.getenv("APP_HOST") + "- CRITICAL External DB has been disabled"
            body = f"""The schoolbox-external-db-circuit-breaker app has disabled the External DB (Edumate).

Reason: {reason}
HTTP URL: {http_url}
HTTP timeout: {http_timeout}
Max attempts: {max_timeouts}
Current attempts: {current_attempts}

You will need to manually enable it again after investigating Edumate performance.
https://{os.getenv("APP_HOST")}.{os.getenv("DOMAIN")}/adminv2/setting/External+DB

"""
            content = Content("text/plain", body)
            mail = Mail(from_email, to_email, subject, content)
            mail_json = mail.get()
            response = sg.client.mail.send.post(request_body=mail_json)

# Main loop
while True:
    try:
        # Make an HTTP GET request with specified timeout value
        # Disable redirect following to detect authentication failures (302 redirects)
        timestamp = datetime.now()
        response = requests.get(url=http_url, headers=http_headers, timeout=http_timeout, allow_redirects=False)

    except requests.exceptions.ConnectionError as err:
        # DNS failure, refused connection, etc
        print(timestamp, "HTTP CONNECTION ERROR", err)
        pass
        
    except requests.exceptions.Timeout as err:
        # Check which number attempt this is
        if(current_attempts <= max_timeouts):
            # Increment attempts and continue the loop
            current_attempts = current_attempts + 1
            print(timestamp, "ATTEMPT NUMBER", current_attempts)
        else:
            # Circuit breaker
            print(timestamp, "CIRCUIT BREAKER", err)
            disable_external_db(f"Connection timeout after {http_timeout} seconds and {current_attempts} attempts")

    
    except OSError as err:
        print(timestamp, "OS ERROR", err)
        pass
    
    except Exception as err:
        # Other Exceptions
        print(timestamp, "GENERAL ERROR", err)
        pass
        
    else:
        # Check HTTP status code - only 200 is considered successful
        if response.status_code != 200:
            # Non-200 status code indicates failure
            reason = f"HTTP status code {response.status_code}"
            if response.status_code == 302:
                redirect_location = response.headers.get('Location', 'N/A')
                reason = f"HTTP status code {response.status_code} (redirect to {redirect_location})"
            elif response.status_code == 401:
                reason = f"HTTP status code {response.status_code} (authentication failure)"
            elif response.status_code == 403:
                reason = f"HTTP status code {response.status_code} (forbidden)"
            elif response.status_code == 404:
                reason = f"HTTP status code {response.status_code} (not found)"
            elif response.status_code >= 500:
                reason = f"HTTP status code {response.status_code} (server error)"
            
            # Check which number attempt this is
            if(current_attempts <= max_timeouts):
                # Increment attempts and continue the loop
                current_attempts = current_attempts + 1
                print(timestamp, "HTTP ERROR:", reason, "ATTEMPT NUMBER", current_attempts)
            else:
                # Circuit breaker
                print(timestamp, "CIRCUIT BREAKER - HTTP ERROR:", reason)
                disable_external_db(reason)
        else:
            # Nothing went wrong, reset attempts
            current_attempts = 1
            # Debug HTTP response times
            if(int(os.getenv("DEBUG_ENABLED"))):
                print(timestamp, "HTTP status code:", response.status_code, "elapsed:", response.elapsed, "attempts:", current_attempts)

    time.sleep(check_frequency)  # Pause execution before trying again
