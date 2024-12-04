import pytest
from pytest_mock import MockerFixture
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.models import VoiceItem, APIResponse, TTSResponse, to_dict
from pydantic import BaseModel
import uuid


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


def test_get_voices(client: Neuphonic, mocker: MockerFixture):
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


def test_delete_voice(client: Neuphonic, mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.is_success = True

    voice_id = 'ec8722cf-a44f-492e-90a6-0412658a64df'
    return_value = {
        'data': {
            'message': f'Voice has successfully been cloned with id {voice_id}',
            'voice_id': voice_id,
        }
    }

    mock_response.json.return_value = return_value
    mock_delete = mocker.patch('httpx.delete', return_value=mock_response)
    delete_response = client.voices.delete(voice_id)

    class DeleteVoiceResponse(BaseModel):
        class Data(BaseModel):
            message: str
            voice_id: str

        data: Data

    delete_voice_response = DeleteVoiceResponse(**delete_response)


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
