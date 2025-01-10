from typing import List, Optional

import httpx

from ._endpoint import Endpoint
from .models import APIResponse, VoiceObject  # noqa: F401


class Voices(Endpoint):
    def get(self) -> APIResponse[dict]:
        """Lists all voices in your voice library.

        Returns
        -------
        APIResponse[dict]
            response.data['voices'] will be a list of VoiceObject objects.
        """
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

        return APIResponse(**response.json())

    def _get_voice_id_from_name(self, voice_name) -> str:
        """Gets the voice_id given a voice name.

        Parameters
        ----------
        voice_name : str
            The name of the voice to retrieve the voice_id for.

        Raises
        ------
        ValueError
            Raised if there is no voice with the provided name.
        """
        response = self.get()
        voices = response.data['voices']

        try:
            # extract the voice_id for the requested voice from the list of all voices
            return next(voice['id'] for voice in voices if voice['name'] == voice_name)
        except StopIteration as e:
            raise ValueError(f'No voice found with the name {voice_name}.')

    def voice(self, voice_id: str = None, voice_name: str = None) -> APIResponse[dict]:
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
        if not voice_id:
            voice_id = self._get_voice_id_from_name(voice_name=voice_name)

        response = httpx.get(
            f'{self.http_url}/voices/{voice_id}',
            headers=self.headers,
            timeout=self.timeout,
        )

        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to fetch voice. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        return APIResponse(**response.json())

    def clone(
        self, voice_name: str, voice_file_path: str, voice_tags: List[str] = []
    ) -> APIResponse[dict]:
        """
        Clone a voice by uploading a file with the specified name and tags.

        Parameters
        ----------
        voice_name : str
            The name of the new cloned voice.
        voice_file_path : str
            Path to the voice file (e.g., a .wav file) to be uploaded.
        voice_tags : List[str]
            Tags associated with the voice. Default is an empty list.

        Returns
        -------
        APIResponse[dict]
            response.data will contain a success message with voice_id of the cloned voice.

        Raises
        ------
        httpx.HTTPStatusError
            If the request to clone the voice fails.
        """

        # Convert voice tags to a string
        if voice_tags:
            voice_tags = (', ').join(voice_tags)

        # Prepare the multipart form-data payload
        params = {
            'voice_tags': voice_tags,
        }
        files = {'voice_file': open(voice_file_path, 'rb')}

        # Send the POST request with voice_name as a query parameter
        response = httpx.post(
            f'{self.http_url}/voices?voice_name={voice_name}',
            params=params,
            files=files,
            headers=self.headers,
            timeout=self.timeout,
        )

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to clone voice. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        # Return the JSON response content as a dictionary
        return APIResponse(**response.json())

    def update(
        self,
        voice_id: Optional[str] = None,
        voice_name: Optional[str] = None,
        new_voice_file_path: Optional[str] = None,
        new_voice_name: str = '',
        new_voice_tags: Optional[List[str]] = None,
    ) -> APIResponse[dict]:
        """
        Update a voice by its ID or name.

        Parameters
        ----------
        voice_id : Optional[str]
            The ID of the voice to update.
        voice_name : Optional[str]
            The name of the voice to update. This does not need to be provided if voice_id
            is provided.
        new_voice_file_path: Optional[str]
            The file path for the new audio file to use for the cloned voice.
        new_voice_name: str
            The new name updated name for the voice.
        new_voice_tags: Optional[List[str]]
            The new tags for the voice.

        Returns
        -------
        APIResponse[dict]
            response.data will contain a success message with the updated fields of the voice.

        Raises
        ------
        httpx.HTTPStatusError
            If the request to update the voice fails. This will usually trigger if you do not have
            permissions to update the voice.
        """

        # Accept case if user only provide name
        if not voice_id:
            try:
                voice_id = self._get_voice_id_from_name(voice_name=voice_name)
            except ValueError as e:
                raise ValueError(
                    f'No voice found with the name {voice_name}. You cannot update this voice.'
                )

        # Convert voice tags to a string
        if new_voice_tags:
            new_voice_tags = (', ').join(new_voice_tags)

        # If voice_file is not given
        if new_voice_file_path is None:
            params = {
                'new_voice_tags': new_voice_tags,
                'new_voice_file': new_voice_file_path,
            }
            files = {}

        # If voice file is given
        else:
            params = {
                'new_voice_tags': new_voice_tags,
            }
            files = {'new_voice_file': open(new_voice_file_path, 'rb')}

        # Call API
        response = httpx.patch(
            f'{self.http_url}/voices/{voice_id}?new_voice_name={new_voice_name}',
            params=params,
            headers=self.headers,
            timeout=self.timeout,
            files=files,
        )

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to update voice. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        # Return the JSON response content as a dictionary
        return APIResponse(**response.json())

    def delete(self, voice_id: str = None, voice_name=None) -> APIResponse[dict]:
        """
        Delete a voice by its ID.

        Parameters
        ----------
        voice_id : str
            The ID of the voice to be deleted.

        Returns
        -------
        APIResponse[dict]
            response.data will contain a success message with the updated fields of the voice.

        Raises
        ------
        httpx.HTTPStatusError
            If the request to delete the voice fails. This will usually trigger if you do not have
            permissions to delete the voice.
        """
        if not voice_id:
            try:
                voice_id = self._get_voice_id_from_name(voice_name=voice_name)
            except ValueError as e:
                raise ValueError(
                    f'No voice found with the name {voice_name}. You cannot Delete this voice.'
                )

        response = httpx.delete(
            f'{self.http_url}/voices/{voice_id}',
            headers=self.headers,
            timeout=self.timeout,
        )

        # Handle response errors
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'Failed to delete voice. Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

        # Return the JSON response content as a dictionary
        return APIResponse(**response.json())
