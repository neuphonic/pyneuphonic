import httpx
from typing import Generator, Union

from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import TTSConfig, APIResponse, TTSResponse, to_dict


class LongformInference(Endpoint):
    def get(self, job_id) -> APIResponse[dict]:
        """Retrieve the status of a longform TTS job by its job ID.
        Parameters
        ----------
        job_id : str
            The unique identifier for the longform TTS job.
        Returns
        -------
        APIResponse[dict]
            An APIResponse object containing the status and details of the longform TTS job.
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

        Returns
        -------
        APIResponse[TTSResponse]
            An APIResponse object containing the status and details of the longform TTS job.
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
