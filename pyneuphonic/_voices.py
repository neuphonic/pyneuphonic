from typing import List

import httpx

from ._endpoint import Endpoint
from .models import VoiceData


class Voices(Endpoint):
    def get(self) -> List[VoiceData]:
        """List all the voices."""
        response = httpx.get(
            f'{self.http_url}/voices',
            headers=self.headers,
            timeout=self.timeout,
        )

        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to fetch voices. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        voices = response.json()['data']['voices']

        return voices
