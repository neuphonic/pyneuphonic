from pydantic import BaseModel as BaseModel, field_validator, ConfigDict
from typing import List, Optional, Callable, Awaitable, Union
import base64
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar('T')


class BaseConfig(BaseModel):
    model_config = ConfigDict(extra='allow')

    def to_query_params(self) -> str:
        """Generate a query params string from the AgentConfig object, dropping None values."""
        params = to_dict(self)
        return '&'.join(f'{key}={value}' for key, value in params.items())


class AgentConfig(BaseConfig):
    agent_id: Optional[str] = None
    endpointing: float = 50
    sampling_rate: int = 16000
    mode: str = 'asr-llm-tts'


class TTSConfig(BaseConfig):
    """
    See https://docs.neuphonic.com/api-reference#options for all available options
    """

    speed: Optional[float] = 1.0
    temperature: Optional[float] = 0.5
    model: Optional[str] = 'neu_fast'
    voice: Optional[str] = None  # if None, default is used.
    sampling_rate: Optional[int] = 22050
    encoding: Optional[str] = 'pcm_linear'
    language_id: Optional[str] = 'en'


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
    model_config['protected_namespaces'] = ()

    id: str
    name: str
    tags: List[str] = []
    model_availability: List[str] = []


class VoicesResponse(BaseModel):
    """Response from /voices endpoint."""

    model_config = ConfigDict(extra='allow')

    class VoicesData(BaseModel):
        voices: List[VoiceItem]

    data: VoicesData


class AudioResponse(BaseModel):
    model_config = ConfigDict(extra='allow')

    audio: Optional[bytes] = None

    @field_validator('audio', mode='before')
    def validate(cls, v: Optional[Union[str, bytes]]) -> Optional[bytes]:
        """Convert the received audio from the server into bytes that can be played."""
        if isinstance(v, str):
            return base64.b64decode(v)
        elif isinstance(v, bytes):
            return v
        elif v is None:
            return None

        raise ValueError('`audio` must be a base64 encoded string or bytes.')


class TTSResponse(AudioResponse):
    """Structure of data received from TTS endpoints, when using any client in`Neuphonic.tts.`"""

    text: Optional[str] = None
    sampling_rate: Optional[int] = None


class AgentResponse(AudioResponse):
    type: str
    text: Optional[str] = None


class APIResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(extra='allow')

    status_code: Optional[int] = None  # only set on SSE responses
    data: T


class SSERequest(BaseModel):
    """Structure of request when using SSEClient or AsyncSSEClient."""

    model_config = ConfigDict(extra='allow')

    text: str
    model: TTSConfig


class WebsocketEventHandlers(BaseModel):
    open: Optional[Callable[[], Awaitable[None]]] = None
    message: Optional[Callable[[APIResponse[T]], Awaitable[None]]] = None
    close: Optional[Callable[[], Awaitable[None]]] = None
    error: Optional[Callable[[Exception], Awaitable[None]]] = None


# --- Deprecated ---
class WebsocketResponse(BaseModel):
    """DEPRECATED. Structure of responses when using AsyncWebsocketClient"""

    model_config = ConfigDict(extra='allow')
    data: TTSResponse


class SSEResponse(BaseModel):
    """DEPRECATED. Structure of response when using SSEClient or AsyncSSEClient."""

    model_config = ConfigDict(extra='allow')

    status_code: int
    data: TTSResponse
