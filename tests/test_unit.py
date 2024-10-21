from unittest.mock import patch
from pyneuphonic.models import VoiceItem


def test_get_voices(client, mocker):
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

    with patch('httpx.get', return_value=mock_response):
        voices = client.voices.get()

        assert len(voices) == 3

        for voice in voices:
            assert isinstance(voice, VoiceItem)
