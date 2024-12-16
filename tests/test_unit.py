import os
import pytest
import tempfile
import wave
from pytest_mock import MockerFixture
from pydantic import BaseModel
import uuid
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.models import VoiceItem, APIResponse, TTSResponse, to_dict

from unittest.mock import MagicMock


def test_tts_config():
    tts_config = TTSConfig(model='neu_fast', temperature=0.8)
    query_param_string = tts_config.to_query_params()

    assert 'model=neu_fast' in query_param_string
    assert 'temperature=0.8' in query_param_string


def test_to_dict():
    dict_repr = to_dict(TTSConfig())

    assert 'voice' not in dict_repr


def test_sse_sync(client: Neuphonic, mocker: MockerFixture):
    sse_client = client.tts.SSEClient()

    mock_stream = mocker.patch('httpx.stream')

    mock_response = mocker.Mock()
    mock_response.iter_lines.return_value = iter(
        [
            'event: message',
            'data: {"status_code": 200, "data": {"audio": "test"}}',
            'event: message',
            'data: {"status_code": 200, "data": {"audio": "test"}}',
            'event: message',
            'data: {"status_code": 200, "data": {"audio": "test"}}',
        ]
    )

    mock_stream.return_value.__enter__.return_value = mock_response

    response = sse_client.send('This is a test.')

    count = 0

    for item in response:
        assert isinstance(item, APIResponse[TTSResponse])
        count += 1

    assert count == 3

    mock_stream.assert_called_once_with(
        method='POST',
        url=f'{sse_client.http_url}/sse/speak/en',
        headers=sse_client.headers,
        json={'text': 'This is a test.', 'model': to_dict(TTSConfig())},
    )


@pytest.mark.asyncio
async def test_websocket_async(client: Neuphonic, mocker: MockerFixture):
    ws = client.tts.AsyncWebsocketClient()

    mock_connect = mocker.patch('websockets.connect', new_callable=mocker.AsyncMock)

    assert ws._ws is None
    await ws.open()
    ssl_context = mock_connect.call_args.kwargs['ssl']
    mock_connect.assert_called_with(
        f'{ws.ws_url}/speak/en?{TTSConfig().to_query_params()}',
        ssl=ssl_context,
        extra_headers=ws.headers,
    )
    await ws.close()

    tts_config = TTSConfig(model='neu_fast', temperature=0.8)
    await ws.open(tts_config=tts_config)
    ssl_context = mock_connect.call_args.kwargs['ssl']
    mock_connect.assert_called_with(
        f'{ws.ws_url}/speak/en?{tts_config.to_query_params()}',
        ssl=ssl_context,
        extra_headers=ws.headers,
    )
    await ws.close()


@pytest.mark.asyncio
async def test_get_voices(client: Neuphonic, mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.is_success = True

    return_value = {
        'data': {
            'voices': [
                {
                    'id': 'b61a1969-07c9-4d10-a055-090bad4fd08e',
                    'name': 'Holly',
                    'tags': ['Female', 'American'],
                },
                {
                    'id': '3752be08-40a1-4ad8-8266-86499c2ed51e',
                    'name': 'Marcus',
                    'tags': ['Male'],
                },
                {
                    'id': '3752be08-40a1-4ad8-8266-86499c2ed51e',
                    'name': 'Damien',
                    'tags': ['Male'],
                },
            ]
        }
    }

    mock_response.json.return_value = return_value
    mock_get = mocker.patch('httpx.get', return_value=mock_response)

    voices = client.voices.get()

    assert len(voices) == 3

    for voice in voices:
        assert isinstance(voice, VoiceItem)


class CloneVoiceResponse(BaseModel):
    class Data(BaseModel):
        message: str
        voice_id: str

    data: Data


@pytest.mark.asyncio
async def test_clone_voice(client: Neuphonic, mocker: MockerFixture):
    # Set up inputs
    voice_name = 'TestVoice-SDK'
    voice_tags = ['tag1', 'tag2']
    voice_tags_adapted = '{tag1, tag2}'

    # Mock the file content
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        voice_file_path = temp_file.name

    try:
        # Create a valid .wav file
        with wave.open(voice_file_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 16-bit samples
            wav_file.setframerate(44100)  # 44.1 kHz sample rate
            wav_file.writeframes(b'\x00\x00' * 44100)  # 1 second of silence

        # Mock the httpx.post response
        mock_post = mocker.patch('httpx.post')

        # Configure the mock response
        mock_response = mocker.Mock()
        mock_response.json.return_value = {
            'data': {
                'message': 'Voice has successfully been cloned.',
                'voice_id': '12345',
            }
        }
        mock_post.return_value = mock_response

        # Call the clone method
        response = client.voices.clone(voice_name, voice_file_path, voice_tags)
        clone_voice_response = CloneVoiceResponse(**response)

        # Assertions
        assert (
            'Voice has successfully been cloned.' in clone_voice_response.data.message
        )
        assert clone_voice_response.data.voice_id == '12345'

        # Ensure httpx.post was called with correct parameters
        base_url = os.getenv('NEUPHONIC_API_URL', 'default-api-url')
        mock_post.assert_called_once_with(
            f'https://{base_url}/voices/clone?voice_name={voice_name}',
            data={'voice_tags': voice_tags_adapted},
            files={'voice_file': mocker.ANY},  # Matches the file object
            headers={'x-api-key': mocker.ANY},  # Ensure the API key is present
            timeout=10,
        )
    finally:
        # Clean up the temporary file
        os.remove(voice_file_path)


def test_delete_voice(client: Neuphonic, mocker: MockerFixture):
    # Initialise mocker
    mock_response = mocker.Mock()
    mock_response.is_success = True  # Simulate a successful deletion

    voice_id = 'ec8722cf-a44f-492e-90a6-0412658a64df'
    return_value = {
        'data': {
            'message': 'Voice was successfully deleted',  # Correct message
            'voice_id': voice_id,
        }
    }

    mock_response.json.return_value = return_value

    # Initialise Patcher
    mock_delete = mocker.patch('httpx.delete', return_value=mock_response)

    # Delete Voice
    delete_response = client.voices.delete(voice_id)

    # Assert the HTTP method and endpoint were called correctly
    base_url = os.getenv('NEUPHONIC_API_URL')
    mock_delete.assert_called_once_with(
        f'https://{base_url}/voices/clone?voice_id={voice_id}',
        headers={'x-api-key': mocker.ANY},  # Ensures api key was present
        timeout=10,
    )

    # Deserialize response into the correct response model
    delete_voice_response = CloneVoiceResponse(**delete_response)

    # Check the response message
    assert 'Voice was successfully deleted' in delete_voice_response.data.message
    assert delete_voice_response.data.voice_id == voice_id


# Example of a test where the HTTP post is mocked
def test_restore_with_transcript_file_success(client: Neuphonic, mocker: MockerFixture):
    # Mock the response of httpx.post
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {'status': 'success', 'job_id': '1234'}

    mock_http_post = mocker.patch('httpx.post', autospec=True)
    mock_http_post.return_value = mock_response

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        audio_path = temp_file.name

    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        transcript_file = temp_file.name

    result = client.restorations.restore(
        audio_path, transcript_file, is_transcript_file=True
    )

    assert result['status'] == 'success'
    assert result['job_id'] == '1234'


# Example of a test where the HTTP post is mocked
def test_restore_with_transcript_string_success(
    client: Neuphonic, mocker: MockerFixture
):
    # Mock the response of httpx.post
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {'status': 'success', 'job_id': '1234'}

    mock_http_post = mocker.patch('httpx.post', autospec=True)
    mock_http_post.return_value = mock_response

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        audio_path = temp_file.name

    result = client.restorations.restore(
        audio_path, 'transcript.txt', is_transcript_file=False
    )

    assert result['status'] == 'success'
    assert result['job_id'] == '1234'


# Example of a test where the HTTP post is mocked
def test_restore_with_transcript_string_failure(
    client: Neuphonic, mocker: MockerFixture
):
    # Mock the response of httpx.post
    mock_response = MagicMock()
    mock_response.is_success = True
    # mock_response.json.return_value = {"status": "success", "job_id": "1234"}

    mock_http_post = mocker.patch('httpx.post', autospec=True)
    mock_http_post.return_value = mock_response

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        audio_path = temp_file.name

    with pytest.raises(ValueError, match='No valid file found at the provided path.'):
        client.restorations.restore(
            audio_path, 'transcript.txt', is_transcript_file=True
        )


def test_restore_get(client: Neuphonic, mocker: MockerFixture):
    # Mock the response of httpx.post
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {'status': 'Finished', 'job_id': '1234'}

    mock_http_post = mocker.patch('httpx.get', autospec=True)
    mock_http_post.return_value = mock_response

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        audio_path = temp_file.name

    result = client.restorations.get(job_id='1234')

    assert result['status'] == 'Finished'


class AgentResponse(BaseModel):
    class Data(BaseModel):
        message: str
        id: str

    data: Data


def test_create_agent(client: Neuphonic, mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.is_success = True
    random_uuid = str(uuid.uuid4())

    return_value = {
        'data': {
            'message': 'Agent successfully created.',
            'id': random_uuid,
        }
    }

    mock_response.json.return_value = return_value
    mock_create = mocker.patch('httpx.post', return_value=mock_response)

    data = {
        'name': 'test_create_agent',
        'prompt': 'You are a helpful agent.',
        'greeting': None,
    }

    create_response = client.agents.create(**data)

    create_response = AgentResponse(**create_response)
    assert create_response.data.id == random_uuid

    mock_create.assert_called_once_with(
        f'https://{client._base_url}/agents',
        json=data,
        headers={'x-api-key': client._api_key},
        timeout=mocker.ANY,
    )


def test_delete_agent(client: Neuphonic, mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.is_success = True
    random_uuid = str(uuid.uuid4())

    return_value = {
        'data': {
            'message': 'Agent successfully deleted.',
            'id': random_uuid,
        }
    }

    mock_response.json.return_value = return_value
    mock_delete = mocker.patch('httpx.delete', return_value=mock_response)

    delete_response = client.agents.delete(agent_id=random_uuid)

    delete_response = AgentResponse(**delete_response)
    assert delete_response.data.id == random_uuid

    mock_delete.assert_called_once_with(
        f'https://{client._base_url}/agents/{random_uuid}',
        headers={'x-api-key': client._api_key},
        timeout=mocker.ANY,
    )


def test_list_agents(client: Neuphonic, mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.is_success = True

    random_uuid_1 = str(uuid.uuid4())
    random_uuid_2 = str(uuid.uuid4())

    return_value = {
        'data': {
            'agents': [
                {'id': random_uuid_1, 'name': 'Agent 1'},
                {'id': random_uuid_2, 'name': 'Agent 2'},
            ]
        }
    }

    mock_response.json.return_value = return_value
    mock_get = mocker.patch('httpx.get', return_value=mock_response)

    get_response = client.agents.get()
    assert get_response['data']['agents'][0]['id'] == random_uuid_1
    assert get_response['data']['agents'][1]['id'] == random_uuid_2

    mock_get.assert_called_once_with(
        f'https://{client._base_url}/agents',
        headers={'x-api-key': client._api_key},
        timeout=mocker.ANY,
    )


def test_list_single_agent(client: Neuphonic, mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.is_success = True
    random_uuid = str(uuid.uuid4())

    return_value = {
        'data': {
            'agent': {
                'id': random_uuid,
                'name': 'Agent 1',
                'prompt': 'You are a helpful agent.',
                'greeting': 'Hi, how can I help you today?',
            },
        }
    }

    mock_response.json.return_value = return_value
    mock_get = mocker.patch('httpx.get', return_value=mock_response)

    get_response = client.agents.get(agent_id=random_uuid)
    assert get_response['data']['agent']['id'] == random_uuid

    mock_get.assert_called_once_with(
        f'https://{client._base_url}/agents/{random_uuid}',
        headers={'x-api-key': client._api_key},
        timeout=mocker.ANY,
    )
