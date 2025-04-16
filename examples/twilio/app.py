from dotenv import load_dotenv
from starlette.websockets import WebSocketState
import logging
import json
import base64
from pyneuphonic import Neuphonic, WebsocketEvents, AgentConfig
from pyneuphonic.models import APIResponse, TTSResponse
import os
from twilio.twiml.voice_response import VoiceResponse, Connect
from fastapi.responses import HTMLResponse
from fastapi import (
    FastAPI,
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Request
)

load_dotenv(override=True)

app = FastAPI()

router = APIRouter()


@app.get('/ping')
def ping():
    return {'message': 'pong'}


@app.api_route("/twilio/inbound_call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response."""
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=f'wss://{os.getenv("SERVER_BASE_URL")}/twilio/agent')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")


@app.websocket('/twilio/agent')
async def agent_websocket(  # noqa: C901
    websocket: WebSocket,
):
    """Handles the WebSocket connection for a Twilio agent, allowing real-time voice conversation."""
    await websocket.accept()
    stream_sid = None

    client = Neuphonic(api_key=os.getenv('NEUPHONIC_API_KEY'))
    neuphonic_agent_websocket = client.agents.AsyncWebsocketClient()

    async def on_message(message: APIResponse[TTSResponse]):
        """Handles messages that are returned from the Neuphonic server to the websocket client."""
        if stream_sid is not None and message.data.type == 'audio_response':
            # Forward audio to the users's phone
            await websocket.send_json(
                {
                    'event': 'media',
                    'streamSid': stream_sid,
                    'media': {
                        'payload': base64.b64encode(message.data.audio).decode('utf-8')
                    },
                }
            )
        elif message.data.type == 'user_transcript':
            logging.info(f'user_transcript: {message.data.text}')
        elif message.data.type == 'llm_response':
            logging.info(f'llm_response: {message.data.text}')
        elif message.data.type == 'stop_audio_response':
            # If the user interrupts then stop playing any currently queued audio
            if stream_sid is not None:
                await websocket.send_json(
                    {
                        'event': 'clear',
                        'streamSid': stream_sid,
                    }
                )

    neuphonic_agent_websocket.on(WebsocketEvents.MESSAGE, on_message)

    await neuphonic_agent_websocket.open(
        agent_config=AgentConfig(
            incoming_sampling_rate=8000,
            return_sampling_rate=8000,
            incoming_encoding='pcm_mulaw',
            return_encoding='pcm_mulaw',
            voice_id='fc854436-2dac-4d21-aa69-ae17b54e98eb',
        )
    )

    try:
        while websocket.client_state == WebSocketState.CONNECTED:
            message = await websocket.receive()

            if message is None or message['type'] == 'websocket.disconnect':
                continue

            data = json.loads(message['text'])

            if data['event'] == 'connected':
                logging.info(f'Connected Message received: {message}')

            if data['event'] == 'start':
                stream_sid = data['start']['streamSid']

            if data['event'] == 'media':
                # Send incoming audio to the Neuphonic agent
                await neuphonic_agent_websocket.send(
                    {'audio': data['media']['payload']}
                )

            if data['event'] == 'closed':
                logging.info(f'Closed Message received: {message}')
                break
    except WebSocketDisconnect as e:
        logging.error(f'WebSocketDisconnect: {e}')
    except Exception as e:
        logging.error(f'Error occured: {e}')
    finally:
        await neuphonic_agent_websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
