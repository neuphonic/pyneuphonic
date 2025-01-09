from pydantic import BaseModel as BaseModel, field_validator, ConfigDict, Field
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
    """
    API parameters passed to the /agent endpoint.
    """

    agent_id: Optional[str] = Field(
        default=None,
        description='Id of selected agent. If none, then a default agent will be used.',
        examples=[
            'da78ea32-9225-436e-b10d-d5b101bb01a6'
        ],  # note - this is not a real agent_id
    )

    endpointing: Optional[float] = Field(
        default=None,
        description=(
            'This is how long (in milliseconds) the speech recognition program will listen for '
            'silence in the recieved audio until it decides that the user is finished speaking.'
        ),
        examples=[50, 100, 1000],
    )

    mode: Optional[str] = Field(
        default='asr-llm-tts',
        description=(
            'This option decides how you want to use the agent. `asr-llm-tts` option indicates that '
            'you want to do audio in, audio out. `llm-tts` indicates that you want to do text in, '
            'audio out.'
        ),
        examples=['asr-llm-tts', 'llm-tts'],
    )

    sampling_rate: int = 16000

    incoming_sampling_rate: Optional[int] = Field(
        default=16000,
        description=(
            'Sampling rate of the audio sent to the server. Lower sampling raes will generally '
            'yield faster transcription.'
        ),
        examples=[8000, 16000, 22050],
    )

    outgoing_sampling_rate: Optional[int] = Field(
        default=22050,
        description='Sampling rate of the audio returned from the server.',
        examples=[8000, 16000, 22050],
    )

    incoming_encoding: Optional[str] = Field(
        default='pcm_linear',
        description='Encoding of the audio sent to the server.',
        examples=['pcm_linear', 'pcm_mulaw'],
    )

    outgoing_encoding: Optional[str] = Field(
        default='pcm_linear',
        description='Encoding of the audio returned from the server.',
        examples=['pcm_linear', 'pcm_mulaw'],
    )


class TTSConfig(BaseConfig):
    """
    Model parameters passed to the text to speech endpoints.
    """

    speed: Optional[float] = Field(
        default=1.0, description='Playback speed of audio.', examples=[0.7, 1.0, 1.5]
    )

    temperature: Optional[float] = Field(
        deafult=None,
        description='Randomness introduced into the text-to-speech model. Ranges from 0 to 1.0.',
        examples=[0.5, 0.7],
    )

    model: Optional[str] = Field(
        default=None,
        description='The text-to-speech model to use.',
        examples=['neu_fast', 'neu_hq'],
    )

    language_id: str = Field(
        default='en',
        description=('Language id for the desired language.'),
        example=['en'],
    )

    voice: Optional[str] = Field(
        deafult=None,
        description=(
            'The voice_id for the desired voice. Ensure that this voice_id is available for the '
            'selected model.'
        ),
        examples=['8e9c4bc8-3979-48ab-8626-df53befc2090'],
    )

    sampling_rate: Optional[int] = Field(
        default=22050,
        description='Sampling rate of the audio returned from the server.',
        examples=[8000, 16000, 22050],
    )

    encoding: Optional[str] = Field(
        default='pcm_linear',
        description='Encoding of the audio returned from the server.',
        examples=['pcm_linear', 'pcm_mulaw'],
    )


class WebsocketEvents(Enum):
    """
    Enum describing all of the valid websocket events that callbacks can be bound to.
    """

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

    data: Optional[T] = Field(
        default=None,
        description='API response data. This will contain data on a succesful response.',
    )

    metadata: Optional[dict] = Field(
        default=None, description='Additional metadata from the API.'
    )

    """
    The below two fields only exist for responses from SSE endpoints.
    """
    status_code: Optional[int] = Field(
        default=None,
        description=(
            'Status code of API response. This is only set for responses on the SSE endpoints.'
        ),
        examples=[200, 400],
    )

    errors: Optional[List[str]] = Field(
        default=None,
        description=(
            'All errors associated with the SSE response, if the status_code is a non 2XX code.'
        ),
    )


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
