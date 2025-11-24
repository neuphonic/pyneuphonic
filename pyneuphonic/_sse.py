import httpx
import json
from typing import Generator, AsyncGenerator, Optional, Union
from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import TTSConfig, APIResponse, TTSResponse, to_dict


class SSEClientBase(Endpoint):
    """Contains shared functions used by both the SSEClient and the AsyncSSE Client."""

    def _parse_message(self, message: str) -> Optional[APIResponse[TTSResponse]]:
        """
        Parse each response from the server and return it as an APIResponse object.

        The message will either be:
        - `event: error`
        - `event: message`
        - `data: { "status_code": 200, "data": {"audio": ... } }`
        """
        message = message.strip()

        if not message or "data" not in message:
            return None

        _, value = message.split(": ", 1)
        message = APIResponse[TTSResponse](**json.loads(value))

        if message.errors is not None:
            raise Exception(
                f"Status {message.status_code} error received: {message.errors}."
            )

        return message


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

        response = super().post(
            endpoint="/sse/auth",
            message="Failed to authenticate for a JWT.",
        )

        jwt_token = response.json()["data"]["jwt_token"]

        self.headers["Authorization"] = f"Bearer: {jwt_token}"

    def send(
        self,
        text: str,
        tts_config: Union[TTSConfig, dict] = TTSConfig(),
        timeout: float = 20,
    ) -> Generator[APIResponse[TTSResponse], None, None]:
        """
        Send a text to the TTS (text-to-speech) service and receive a stream of APIResponse messages.

        Parameters
        ----------
        text : str
            The text to be converted to speech.
        tts_config : Union[TTSConfig, dict], optional
            The TTS configuration settings. Can be an instance of TTSConfig or a dictionary which
            will be parsed into a TTSConfig.
        timeout : Optional[float]
            The timeout in seconds for the request.

        Yields
        ------
        Generator[APIResponse[TTSResponse], None, None]
            A generator yielding APIResponse messages.
        """
        if not isinstance(tts_config, TTSConfig):
            tts_config = TTSConfig(**tts_config)

        assert isinstance(text, str), "`text` should be an instance of type `str`."

        with httpx.stream(
            method="POST",
            url=f"{self.http_url}/sse/speak/{tts_config.lang_code}",
            headers=self.headers,
            json={"text": text, **to_dict(tts_config)},
            timeout=timeout,
        ) as response:
            for message in response.iter_lines():
                parsed_message = self._parse_message(message)

                if parsed_message is not None:
                    yield parsed_message


class AsyncSSEClient(SSEClientBase):
    async def jwt_auth(self) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.http_url}/sse/auth", headers=self.headers, timeout=self.timeout
            )

            self.raise_for_status(
                response=response,
                message="Failed to authenticate for a JWT.",
            )

            jwt_token = response.json()["data"]["jwt_token"]
            self.headers["Authorization"] = f"Bearer: {jwt_token}"

    async def send(
        self,
        text: str,
        tts_config: Union[TTSConfig, dict] = TTSConfig(),
        timeout: float = 20,
    ) -> AsyncGenerator[APIResponse[TTSResponse], None]:
        if not isinstance(tts_config, TTSConfig):
            tts_config = TTSConfig(**tts_config)

        assert isinstance(text, str), "`text` should be an instance of type `str`."

        async with httpx.AsyncClient() as client:
            async with client.stream(
                method="POST",
                url=f"{self.http_url}/sse/speak/{tts_config.lang_code}",
                headers=self.headers,
                json={"text": text, **to_dict(tts_config)},
                timeout=timeout,
            ) as response:
                async for message in response.aiter_lines():
                    parsed_message = self._parse_message(message)

                    if parsed_message is not None:
                        yield parsed_message
