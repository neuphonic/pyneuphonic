import httpx
import os

from ._endpoint import Endpoint


class Restore(Endpoint):
    def restore(
        self,
        audio_path: str,
        transcript: str = '',
        lang_code: str = 'eng-us',
    ):
        # if transcript is a path
        if os.path.isabs(transcript):
            files = {
                'audio_file': open(audio_path, 'rb'),
                'transcript': open(transcript, 'rb'),
            }
            data = {'lang_code': lang_code}
        # if transcript is a string
        else:
            files = {'audio_file': open(audio_path, 'rb')}
            data = {'lang_code': lang_code, 'transcript': transcript}

        response = httpx.post(
            f'{self.http_url}/restore/job', files=files, data=data, headers=self.headers
        )

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to queue restoration job. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        # Return the JSON response content as a dictionary
        return response.json()

    def get(self, job_id):
        response = httpx.get(f'{self.http_url}/restore/{job_id}', headers=self.headers)

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to get status of this restoration job. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        # Return the JSON response content as a dictionary
        return response.json()
