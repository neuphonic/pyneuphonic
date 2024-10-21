from pydantic import BaseModel as BaseModel, field_validator, ConfigDict
from typing import List, Literal, Optional, Callable, Awaitable, Union
import base64
from enum import Enum


class TTSConfig(BaseModel):
    speed: float = 1.0
    temperature: float = 0.5
    model: Literal['neu_fast', 'neu_hq'] = 'neu_fast'
    voice: Optional[
        str
    ] = None  # the voice id for the desired voice, if None, default will be used
    sampling_rate: Literal[22050, 8000] = 22050
    encoding: Literal['pcm_linear', 'pcm_mulaw'] = 'pcm_linear'
    language_id: Literal['en'] = 'en'

    def to_query_params(self) -> str:
        """Generate a query params string from the TTSConfig object, dropping None values."""
        params = to_dict(self)
        return '&'.join(f'{key}={value}' for key, value in params.items())


class WebsocketEvents(Enum):
    OPEN: str = 'open'
    MESSAGE: str = 'message'
    CLOSE: str = 'close'
    ERROR: str = 'error'


def to_dict(model: BaseModel):
    """Returns a pydantic model as dict, with all of the None items removed."""
    return {k: v for k, v in model.model_dump().items() if v is not None}


class VoiceItem(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: str
    name: str
    tags: List[str] = None


class VoicesResponse(BaseModel):
    """Response from /voices endpoint."""

    model_config = ConfigDict(extra='allow')

    class VoicesData(BaseModel):
        voices: List[VoiceItem]

    data: VoicesData


class AudioData(BaseModel):
    """Structure of audio data received when using any client."""

    model_config = ConfigDict(extra='allow')

    audio: bytes
    text: Optional[str] = None
    sampling_rate: Optional[int] = None

    @field_validator('audio', mode='before')
    def validate(cls, v: Union[str, bytes]) -> bytes:
        """Convert the received audio from the server into bytes that can be played."""
        if isinstance(v, str):
            return base64.b64decode(v)
        elif isinstance(v, bytes):
            return v

        raise ValueError('`audio` must be a base64 encoded string or bytes.')


class WebsocketResponse(BaseModel):
    """Structure of responses when using AsyncWebsocketClient"""

    model_config = ConfigDict(extra='allow')

    data: AudioData


class SSEResponse(BaseModel):
    """Structure of response when using SSEClient or AsyncSSEClient."""

    model_config = ConfigDict(extra='allow')

    status_code: int
    data: AudioData


class SSERequest(BaseModel):
    """Structure of request when using SSEClient or AsyncSSEClient."""

    model_config = ConfigDict(extra='allow')

    text: str
    model: TTSConfig


class WebsocketEventHandlers(BaseModel):
    open: Optional[Callable[[], Awaitable[None]]] = None
    message: Optional[Callable[[AudioData], Awaitable[None]]] = None
    close: Optional[Callable[[], Awaitable[None]]] = None
    error: Optional[Callable[[Exception], Awaitable[None]]] = None
