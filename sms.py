from twilio.rest import Client
from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

# Twilio account SID and auth token
account_sid = ''
auth_token = ''

# Create a Twilio client object
client = Client(account_sid, auth_token)


@app.post('/send/text')
async def send_text(request: Request, response: Response):
    # data = await request.json()
    # REPLACE WITH REAL MOBILE NUMBER TO AVOID ERROR
    number = "+"
    message = "HELLO OODIE"

    # Send the SMS message using Twilio
    twilio_message = client.messages.create(
        to=number,
        from_='+',  # Replace with your Twilio phone number
        body=message
    )

    response_body = {'message_sid': twilio_message.sid}
    response.content = json.dumps(response_body)
    return response.content
