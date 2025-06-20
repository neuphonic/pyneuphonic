import httpx
import json
from typing import Generator, Optional, Union

from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import TTSConfig, APIResponse, TTSResponse, to_dict


class LongformInference(Endpoint):
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

    def get(self, job_id) -> APIResponse[dict]:
        """Get information about specific voice.

        Parameters
        ----------
        voice_name : str
            The voice name you want to retreive the information for.
        voice_id : str
            The voice id you want to retreive the information for.

        Returns
        -------
        APIResponse[dict]
            response.data['voice'] will be a single VoiceObject object.

        Raises
        ------
        httpx.HTTPStatusError
            If the request to clone the voice fails.
        """

        # Accept case if user only provide name
        if job_id is None:
            raise ValueError("Please provide a job_id")

        response = httpx.get(
            url=f"{self.http_url}/speak/longform?job_id={job_id}",
            headers=self.headers,
            timeout=30,
        )

        return APIResponse(**response.json())

    def post(
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

        response = httpx.post(
            url=f"{self.http_url}/speak/longform",
            headers=self.headers,
            json={"text": text, **to_dict(tts_config)},
            timeout=timeout,
        )

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Failed to post longform inference job. Status code: {response.status_code}. Error: {response.text}",
                request=response.request,
                response=response,
            )

        # Return the JSON response content as a dictionary
        return APIResponse(**response.json())
