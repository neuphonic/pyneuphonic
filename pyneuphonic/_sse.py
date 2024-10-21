import httpx
import json
from typing import Generator, AsyncGenerator, Optional, Union

from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import TTSConfig, SSEResponse, to_dict


class SSEClientBase(Endpoint):
    """Contains shared functions used by both the SSEClient and the AsyncSSE Client."""

    def _parse_message(self, message: str) -> Optional[SSEResponse]:
        """Parse each response from the server. Return as an SSEResponse object."""
        lines = message.split('\n')
        data = {}

        for line in lines:
            if not line.strip():
                continue

            try:
                key, value = line.split(': ', 1)
            except Exception as e:
                raise ValueError(f'Client request was malformed or incorrect: {line}')

            if key == 'data':
                data[key] = value

        if 'data' in data:
            return SSEResponse(**json.loads(data['data']))

        return None


class SSEClient(SSEClientBase):
    def jwt_auth(self) -> None:
        """
        Authenticate with the server to obtain a JWT token.

        This method sends a POST request to the server's authentication endpoint to exchange the
        API key for a JWT token.
        The token is then added to the headers for subsequent requests.
        Using JWT auth for subsequent requests speeds up the time to first audio byte when using
        the SSEClient.send method.
        Using JWT auth is recommended for situations where latency is a priority.

        Raises
        ------
        httpx.HTTPStatusError
            If the authentication request fails, an HTTPStatusError is raised with
            details about the failure.
        """
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

    def send(
        self, text: str, tts_config: Union[TTSConfig, dict] = TTSConfig()
    ) -> Generator[SSEResponse, None, None]:
        """
        Send a text to the TTS (text-to-speech) service and receive a stream of SSEResponse messages.

        Parameters
        ----------
        text : str
            The text to be converted to speech.
        tts_config : Union[TTSConfig, dict], optional
            The TTS configuration settings. Can be an instance of TTSConfig or a dictionary which
            will be parsed into a TTSConfig.

        Yields
        ------
        Generator[SSEResponse, None, None]
            A generator yielding SSEResponse messages.
        """
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
                parsed_message = self._parse_message(message)

                if parsed_message is not None:
                    yield parsed_message


class AsyncSSEClient(SSEClientBase):
    async def jwt_auth(self) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
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

    async def send(
        self, text: str, tts_config: Union[TTSConfig, dict] = TTSConfig()
    ) -> AsyncGenerator[SSEResponse, None]:
        if not isinstance(tts_config, TTSConfig):
            tts_config = TTSConfig(**tts_config)

        assert isinstance(text, str), '`text` should be an instance of type `str`.'

        async with httpx.AsyncClient() as client:
            async with client.stream(
                method='POST',
                url=f'{self.http_url}/sse/speak/{tts_config.language_id}',
                headers=self.headers,
                json={'text': text, 'model': to_dict(tts_config)},
            ) as response:
                async for message in response.aiter_lines():
                    parsed_message = self._parse_message(message)

                    if parsed_message is not None:
                        yield parsed_message
