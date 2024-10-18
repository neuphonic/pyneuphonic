import httpx
import json

from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import TTSConfig, SSERequest, SSEResponse, to_dict


class SSEClient(Endpoint):
    def jwt_auth(self):
        response = httpx.post(
            f'{self.http_url}/sse/auth', headers=self.headers, timeout=self.timeout
        )

        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to authenticate for a JWT. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        jwt_token = response.json()['data']['jwt_token']

        self.headers['Authorization'] = f'Bearer: {jwt_token}'
        del self.headers['X-API-Key']

    @staticmethod
    def _parse_sse_message(message: str) -> SSERequest:
        # Split the message into lines
        lines = message.split('\n')
        data = {}

        for line in lines:
            # Ignore empty lines
            if not line.strip():
                continue

            # Split the line into key and value
            key, value = line.split(': ', 1)

            # Store the value in the data dictionary
            if key == 'data':
                data[key] = value

        if 'data' in data:
            return SSEResponse(**json.loads(data['data']))

        return None

    def send(self, text: str, tts_config: TTSConfig | dict = TTSConfig()):
        if not isinstance(tts_config, TTSConfig):
            tts_config = TTSConfig(**tts_config)

        assert isinstance(text, str), '`text` should be an instance of type `str`.'

        with httpx.stream(
            method='POST',
            url=f'{self.http_url}/sse/speak/{tts_config.language_id}',
            headers=self.headers,
            json={'text': text, 'model': to_dict(tts_config)},
        ) as response:
            for message in response.iter_lines():
                parsed_message = self._parse_sse_message(message)

                if parsed_message is not None:
                    yield parsed_message
