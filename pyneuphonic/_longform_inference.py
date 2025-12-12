from typing import Generator, Union
from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import TTSConfig, APIResponse, to_dict


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
        return super().get(
            id=job_id,
            endpoint="/speak/longform?job_id=",
            message="Failed to fetch longform TTS job status.",
        )

    def post(
        self,
        text: str,
        tts_config: Union[TTSConfig, dict] = TTSConfig(),
    ) -> Generator[APIResponse[dict], None, None]:
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
        APIResponse[dict]
            An APIResponse object containing the status and details of the longform TTS job.
        """
        if not isinstance(tts_config, TTSConfig):
            tts_config = TTSConfig(**tts_config)

        assert isinstance(text, str), "`text` should be an instance of type `str`."

        return super().post(
            data={"text": text, **to_dict(tts_config)},
            endpoint="/speak/longform",
            message="Failed to send text to TTS service.",
        )
