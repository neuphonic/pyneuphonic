from typing import List

import httpx

from ._endpoint import Endpoint


class CloneVoices(Endpoint):
    def post(
        self, voice_name: str, voice_tags: List[str], voice_file_path: str
    ) -> dict:
        """
        Clone a voice by uploading a file with specified name and tags.

        Args:
            voice_name (str): The name of the new cloned voice.
            voice_tags (List[str]): Tags associated with the voice.
            voice_file_path (str): Path to the voice file (e.g., a .wav file) to be uploaded.

        Returns:
            dict: A dictionary with the response data from the API.
        """

        # Prepare the multipart form-data payload
        # Prepare the multipart form-data payload
        data = {
            'voice_tags': voice_tags,
        }
        files = {'voice_file': open(voice_file_path, 'rb')}

        # Send the POST request with voice_name as a query parameter
        response = httpx.post(
            f'{self.http_url}/clone_voice?voice_name={voice_name}',
            data=data,
            files=files,
            headers=self.headers,
            timeout=self.timeout,
        )

        # Handle response errors
        if not response.is_success:
            print(response)
            raise httpx.HTTPStatusError(
                f'Failed to clone voice. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        # Return the JSON response content as a dictionary
        return response.json()
