# Neuphonic Agents - Twilio Integration Guide

This demo illustrates how to integrate Neuphonic's agent features with Twilio to create an interactive and intelligent phone voice agent capable of handling both inbound and outbound phone calls.

- [Neuphonic Agents - Twilio Integration Guide](#neuphonic-agents---twilio-integration-guide)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
    - [Environment Setup](#environment-setup)
    - [Running the Server](#running-the-server)
  - [Initiate an Outbound Call](#initiate-an-outbound-call)
  - [Next Steps](#next-steps)

## Prerequisites
Before getting started, ensure you have:
- A Neuphonic API Key
- A Twilio account with a Twilio phone number
- Python 3.9 or higher
- A free [ngrok](https://ngrok.com/) account with the ngrok CLI installed and authenticated

## Setup
### Environment Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your environment:
   ```bash
   cp .env.example .env
   ```

   Add the following variables to your `.env` file:
   - `NEUPHONIC_API_KEY`: Found on the [Neuphonic portal](https://app.neuphonic.com/)
   - `TWILIO_AUTH_TOKEN` and `TWILIO_ACCOUNT_SID`: Available in your Twilio portal
   - `FROM_NUMBER`: Your Twilio-purchased phone number
   - `TO_NUMBER`: Your personal phone number for receiving test calls

   Leave `SERVER_BASE_URL` blank for now - we'll fill this in the next step.

### Running the Server
The server, built with FastAPI, handles communication between Twilio and Neuphonic. Here's how to get it running:

1. Start ngrok:
   ```bash
   ngrok http http://localhost:8000
   ```

   Copy the displayed URL (excluding the `https://` prefix) and add it to your `.env` file as `SERVER_BASE_URL`. It will look something like `123d-45-678-912-3.ngrok-free.app`.

   <details>
   <summary>About ngrok</summary>
   ngrok securely exposes your local machine's port 8000 to the internet, providing a public URL that Twilio can use to communicate with your server. This is necessary because Twilio needs a secure, publicly accessible endpoint to interact with your application.
   </details>

2. Start the FastAPI server:
   ```bash
   python app.py
   ```

## Initiate an Outbound Call
To test the integration, you can initiate an outbound call from your Twilio number to your personal phone number:
```bash
python make_outbound_call.py
```

## Next Steps
This demo provides a basic introduction to integrating Neuphonic Agents with Twilio. To explore more advanced features and capabilities:

- Check out the [Twilio Voice Documentation](https://www.twilio.com/docs/voice)
- Visit the [Neuphonic Documentation](https://docs.neuphonic.com/quickstart) for additional integration guides and examples
