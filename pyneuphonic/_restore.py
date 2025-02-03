import httpx
import os

from ._endpoint import Endpoint
from .models import APIResponse


class Restore(Endpoint):
    def restore(
        self,
        audio_path: str,
        transcript: str = '',
        lang_code: str = 'eng-us',
        is_transcript_file: bool = False,
    ) -> APIResponse[dict]:
        if is_transcript_file:
            # if transcript is a path
            if os.path.exists(transcript) and os.path.isfile(transcript):
                files = {
                    'audio_file': open(audio_path, 'rb'),
                    'transcript': open(transcript, 'rb'),
                }
                data = {'lang_code': lang_code}
            else:
                raise ValueError('No valid file found at the provided path.')

        # if transcript is a string
        else:
            files = {'audio_file': open(audio_path, 'rb')}
            data = {'lang_code': lang_code, 'transcript': transcript}

        response = httpx.post(
            f'{self.http_url}/restore', files=files, data=data, headers=self.headers
        )

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to queue restoration job. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        return APIResponse(**response.json())

    def list(self) -> APIResponse[dict]:
        response = httpx.get(f'{self.http_url}/restore', headers=self.headers)

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to get status of this restoration job. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        return APIResponse(**response.json())

    def get(self, job_id=None) -> APIResponse[dict]:
        response = httpx.get(f'{self.http_url}/restore/{job_id}', headers=self.headers)

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to get status of this restoration job. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        return APIResponse(**response.json())

    def download(self, job_id=None, file_path=None) -> None:
        response = httpx.get(f'{self.http_url}/restore/{job_id}', headers=self.headers)
        url = response.json()['data']['file_url']

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to download the restored audio. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        response = httpx.get(url)

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to download the restored audio. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        with open(file_path, 'wb') as f:
            f.write(response.content)

    def delete(self, job_id=None) -> APIResponse[dict]:
        response = httpx.delete(f'{self.http_url}/restore/{job_id}', headers=self.headers)

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to delete this restoration job. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        return APIResponse(**response.json())
