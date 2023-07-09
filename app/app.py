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
http_timeout = float(os.getenv("HTTP_TIMEOUT"))
check_frequency = int(os.getenv("CHECK_FREQUENCY"))
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

while True:
    try:
        # Make an HTTP GET request with specified timeout value
        timestamp = datetime.now()
        response = requests.get(url=http_url, headers=http_headers, timeout=http_timeout)

    except requests.exceptions.ConnectionError as err:
        # DNS failure, refused connection, etc
        print(timestamp, "HTTP CONNECTION ERROR", err)
        pass
        
    except requests.exceptions.Timeout as err:
        # Circuit breaker
        print(timestamp, "CIRCUIT BREAKER", err)
        pass

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

        except Exception as err:
            print(timestamp, "DATABASE ERROR", err)
            if(int(os.getenv("EMAIL_ENABLED"))):
                # Send email notification regarding FATAL event
                subject = os.getenv("APP_HOST") + "- FATAL Failed to disable External DB"
                body = "The schoolbox-external-db-circuit-breaker app failed to disable the External DB (Edumate).\n" + str(err)
                content = Content("text/plain", body)
                mail = Mail(from_email, to_email, subject, content)
                mail_json = mail.get()
                response = sg.client.mail.send.post(request_body=mail_json)
            pass

        else:
            print(timestamp, "External DB has been disabled")
            if(int(os.getenv("EMAIL_ENABLED"))):
                # Send email notification regarding CRITICAL event
                subject = os.getenv("APP_HOST") + "- CRITICAL External DB has been disabled"
                body = f"""The schoolbox-external-db-circuit-breaker app has disabled the External DB (Edumate).\n
You will need to manually enable it again after investigating Edumate performance. \n
https://{os.getenv("APP_HOST")}.{os.getenv("DOMAIN")}/adminv2/setting/External+DB"""
                content = Content("text/plain", body)
                mail = Mail(from_email, to_email, subject, content)
                mail_json = mail.get()
                response = sg.client.mail.send.post(request_body=mail_json)

    
    except OSError as err:
        print(timestamp, "OS ERROR", err)
        pass
    
    except Exception as err:
        # Other Exceptions
        print(timestamp, "GENERAL ERROR", err)
        pass
        
    else:
        # Nothing went wrong
        # Debug HTTP response times
        if(int(os.getenv("DEBUG_ENABLED"))):
            print(timestamp, "HTTP response.elapsed:", response.elapsed)

    time.sleep(check_frequency)  # Pause execution before trying again
