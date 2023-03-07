# from twilio.rest import Client
# from fastapi import FastAPI, Request, Response
# from fastapi.responses import JSONResponse
# import json
from twilio.rest import Client
import mysql.connector

# Twilio account SID and auth token
account_sid = ''
auth_token = ''

# Define MySQL connection parameters

db_config = {
    'host': '',
    'database': '',
    'user': '',
    'password': ''
}
# Create a Twilio client object
client = Client(account_sid, auth_token)

# Connect to the MySQL database
try:
    conn = mysql.connector.connect(**db_config)
except mysql.connector.Error as err:
    print("Error connecting to MySQL: {}".format(err))
    exit()

# Query the database for unsent notifications
cursor = conn.cursor(dictionary=True)
query = "SELECT * FROM notification_list WHERE sent = false"
cursor.execute(query)
results = cursor.fetchall()

for result in results:
    recipient = result['phone']
    message = result['message']

    try:
        # Send the SMS message using Twilio
        twilio_message = client.messages.create(
            to=recipient,
            from_='+1',  # Replace with your Twilio phone number
            body=message
        )
        print("Sent SMS to {}: {}".format(recipient, message))

        # Update the notification_list table to mark the message as sent
        query = "UPDATE notification_list SET sent = true WHERE id = %s"
        cursor.execute(query, (result['id'],))
        conn.commit()
    except Exception as e:
        print("Error sending SMS to {}: {}".format(recipient, e))

# Close the database connection
cursor.close()
conn.close()
