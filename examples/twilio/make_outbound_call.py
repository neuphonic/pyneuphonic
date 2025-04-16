"""
This script makes an outbound call using the Twilio API.

It constructs a TWiML message to instruct Twilo to connect make an outgoing call from FROM_NUMBER
to TO_NUMBER and connect it to the websocket server hosted at: {os.getenv("SERVER_BASE_URL")}/twilio/agent

The following environment variables must be set:
- TWILIO_ACCOUNT_SID: The Account SID for Twilio API authentication.
- TWILIO_AUTH_TOKEN: The Auth Token for Twilio API authentication.
- SERVER_BASE_URL: The base URL of the server to connect the call to. This is given to you by ngrok.
- TO_NUMBER: The phone number to call.
- FROM_NUMBER: The phone number from which the call is made, this is the number purchased on Twilio.
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv(override=True)


def make_outbound_call():
    # Initialize the Twilio client with account credentials
    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

    # Construct the TwiML message to connect the call to the WebSocket endpoint
    twiml_message = f'<?xml version="1.0" encoding="UTF-8"?><Response><Connect><Stream url="wss://{os.getenv("SERVER_BASE_URL")}/twilio/agent" /></Connect></Response>'

    # Create the call with the specified parameters
    call = client.calls.create(
        twiml=twiml_message,
        to=os.getenv('TO_NUMBER'),
        from_=os.getenv('FROM_NUMBER'),
        record=True,
    )

    # Print the call SID
    print(call.sid)


if __name__ == '__main__':
    # Execute the make_outbound_call function if the script is run directly
    make_outbound_call()
