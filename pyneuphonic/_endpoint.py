import httpx
from typing import Optional
from pyneuphonic.models import APIResponse


class Endpoint:
    """Base class for all API endpoints.

    Parameters
    ----------
    api_key : str
        The API key for authentication.
    base_url : str
        The base URL for the API.
    timeout : int
        The timeout for API requests in seconds. Default is 10 seconds.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 10,
    ):
        self._api_key = api_key
        self._base_url = base_url
        self.timeout = timeout

        self.headers = {
            "x-api-key": self._api_key,
        }

    @property
    def base_url(self):
        return self._base_url

    def _is_localhost(self):
        return True if "localhost" in self.base_url else False

    @property
    def http_url(self):
        prefix = "http" if self._is_localhost() else "https"
        return f"{prefix}://{self.base_url}"

    @property
    def ws_url(self):
        prefix = "ws" if self._is_localhost() else "wss"
        return f"{prefix}://{self.base_url}"

    def raise_for_status(self, response: httpx.Response, message: Optional[str] = None):
        """
        Raises an `httpx.HTTPStatusError` if the response status code indicates an error.
        Parameters
        ----------
        response : httpx.Response
            The HTTP response to check.
        message : Optional[str]
            An optional message to include in the error.
        Raises
        ------
        httpx.HTTPStatusError
            If the response status code indicates an error.
        """
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f'{message + " " if message is not None else ""}Status code: {response.status_code}. Error: {response.text}',
                request=response.request,
                response=response,
            )

    def get(
        self,
        id: str = "",
        endpoint: str = "",
        message: str = "Failed to fetch.",
    ) -> APIResponse[dict]:
        """
        Fetch items from the API.

        Parameters
        ----------
        id
            The ID of item to fetch.

        Returns
        -------
        APIResponse[dict]
            response.data will be an object of type dict.

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails to fetch.
        """

        response = httpx.get(
            f"{self.http_url}{endpoint}{id}",
            headers=self.headers,
            timeout=self.timeout,
        )

        self.raise_for_status(response=response, message=message)

        return APIResponse(**response.json())

    def post(
        self,
        data: str = None,
        params: dict = None,
        files: dict = None,
        endpoint: str = "",
        message: str = "Failed to create.",
    ) -> APIResponse[dict]:
        """
        Post data to create a new resource.

        Parameters
        ----------
        data : str
            The JSON data to send in the request body.
        params : dict
            The query parameters to include in the request.
        files : dict
            The files to upload in the request.
        endpoint : str
            The API endpoint to send the request to.
        message : str
            The error message to include in the exception if the request fails.

        Returns
        -------
        APIResponse[dict]
            response.data will contain a success message on successful creation.

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails to create.
        """

        response = httpx.post(
            f"{self.http_url}{endpoint}",
            json=data,
            params=params,
            files=files,
            headers=self.headers,
            timeout=self.timeout,
        )

        self.raise_for_status(response=response, message=message)

        return APIResponse(**response.json())

    def delete(
        self,
        id: str,
        endpoint: str,
        message: str = "Failed to delete.",
    ) -> APIResponse[dict]:
        """
        Delete a resource by its ID.

        Parameters
        ----------
        id : str
            The ID of the item to delete.
        endpoint : str
            The API endpoint to send the request to.
        message : str
            The error message to include in the exception if the request fails.

        Returns
        -------
        APIResponse[dict]
            response.data will contain a delete message on successful deletion.

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails to delete.
        """
        response = httpx.delete(
            f"{self.http_url}{endpoint}{id}",
            headers=self.headers,
            timeout=self.timeout,
        )

        self.raise_for_status(response=response, message=message)

        return APIResponse(**response.json())
