from pydantic import BaseModel as BaseModel, field_validator, ConfigDict, Field
from typing import List, Optional, Callable, Awaitable, Union, TypedDict
import base64
from enum import Enum
from typing import Generic, TypeVar


def to_dict(model: BaseModel):
    """Returns a pydantic model as a dictionary, excluding items with None values."""
    return {k: v for k, v in model.model_dump().items() if v is not None}


T = TypeVar('T')


class BaseConfig(BaseModel):
    model_config = ConfigDict(extra='allow')

    def to_query_params(self) -> str:
        """Generate a query parameter string from the object, excluding None values."""
        params = to_dict(self)
        return '&'.join(f'{key}={value}' for key, value in params.items())


class AgentConfig(BaseConfig):
    """
    API parameters for the /agent endpoint.
    """

    agent_id: Optional[str] = Field(
        default=None,
        description='ID of the selected agent. If None, a default agent will be used.',
        examples=['da78ea32-9225-436e-b10d-d5b101bb01a6'],  # example agent_id
    )

    endpointing: Optional[float] = Field(
        default=None,
        description=(
            'Duration (in milliseconds) the speech recognition program will listen for '
            'silence in the received audio before concluding the user has finished speaking.'
        ),
        examples=[50, 100, 1000],
    )

    mode: Optional[str] = Field(
        default='asr-llm-tts',
        description=(
            'Mode of agent usage. `asr-llm-tts` indicates audio input and output. '
            '`llm-tts` indicates text input and audio output.'
        ),
        examples=['asr-llm-tts', 'llm-tts'],
    )

    sampling_rate: int = 16000

    incoming_sampling_rate: Optional[int] = Field(
        default=16000,
        description=(
            'Sampling rate of the audio sent to the server. Lower rates generally '
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
    Model parameters for the text-to-speech endpoints.
    """

    speed: Optional[float] = Field(
        default=1.0,
        description='Playback speed of the audio.',
        examples=[0.7, 1.0, 1.5],
    )

    temperature: Optional[float] = Field(
        default=None,
        description='Randomness introduced into the text-to-speech model. Range: 0 to 1.0.',
        examples=[0.5, 0.7],
    )

    model: Optional[str] = Field(
        default=None,
        description='The text-to-speech model to use.',
        examples=['neu_fast', 'neu_hq'],
    )

    language_id: str = Field(
        default='en',
        description='Language ID for the desired language.',
        examples=['en'],
    )

    voice: Optional[str] = Field(
        default=None,
        description=(
            'The voice ID for the desired voice. Ensure this voice ID is available for the '
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


class APIResponse(BaseModel, Generic[T]):
    """All API responses will be typed with this pydantic model."""

    model_config = ConfigDict(extra='allow')

    data: Optional[T] = Field(
        default=None,
        description='API response data. Contains data on a successful response.',
    )

    metadata: Optional[dict] = Field(
        default=None,
        description=(
            'Additional metadata from the API. Includes pagination metadata for paginated '
            'endpoints.'
        ),
    )

    """
    The following fields are only for responses from SSE endpoints.
    """
    status_code: Optional[int] = Field(
        default=None,
        description=(
            'Status code of the API response. Only set for responses on SSE endpoints.'
        ),
        examples=[200, 400],
    )

    errors: Optional[List[str]] = Field(
        default=None,
        description=(
            'All errors associated with the SSE response, if the status_code is non-2XX.'
        ),
    )


class VoiceObject(TypedDict):
    """TypedDict representing a voice object with its attributes."""

    id: str
    """
    The voice ID.
    Examples: ['8e9c4bc8-3979-48ab-8626-df53befc2090']
    """

    name: str
    """
    The name of the voice.
    Examples: ['Holly', 'Annie', 'Miles']
    """

    tags: List[str]
    """
    A list of tags describing the voice.
    Examples: [['Male', 'American', 'Forties', 'Narrator'], ['Female', 'British', 'Twenties', 'Excited']]
    """

    model_availability: List[str]
    """
    A list of models that this voice is available on.
    Examples: [['neu_fast', 'neu_hq'], ['neu_hq']]
    """

    standard: str
    """
    Indicates whether this is a standard voice provided by Neuphonic, or a cloned voice.
    """


class AgentObject(TypedDict):
    """TypedDict representing an agent object with its attributes."""

    id: str
    """
    The agent ID.
    Examples: ['1234abcd-5678-efgh-9101-ijklmnopqrst']
    """

    name: str
    """
    The name of the agent.
    Examples: ['Helpful Receptionist', 'Delivery Person', 'John Smith']
    """

    prompt: Optional[str]
    """
    The prompt used by the agent.
    Examples: ['You are a helpful agent. Answer in 20 words or less.']
    """

    greeting: Optional[str]
    """
    The greeting message of the agent.
    Examples: ['Hello! How can I help you?', 'Hi there! What can I do for you today?']
    """


class AudioBaseModel(BaseModel):
    """
    Base model for any models containing audio.
    """

    model_config = ConfigDict(extra='allow')

    audio: Optional[bytes] = Field(
        default=None,
        description=(
            'Audio received from the server. The server returns audio as a base64 encoded string, '
            'which will be parsed into bytes by the field_validator.'
        ),
    )

    @field_validator('audio', mode='before')
    def validate(cls, v: Optional[Union[str, bytes]]) -> Optional[bytes]:
        """Convert the received audio from the server from base64 into bytes."""
        if isinstance(v, str):
            return base64.b64decode(v)
        elif isinstance(v, bytes):
            return v
        elif v is None:
            return None

        raise ValueError('`audio` must be a base64 encoded string or bytes.')


class TTSResponse(AudioBaseModel):
    """Structure of data received from TTS endpoints, when using any client in `Neuphonic.tts`."""

    text: Optional[str] = Field(
        default=None, description='Text corresponding to the audio snippet.'
    )

    sampling_rate: Optional[int] = Field(
        default=None,
        description='Sampling rate of the audio snippet.',
        examples=[8000, 16000, 22050],
    )


class AgentResponse(AudioBaseModel):
    """Structure of data received from Agent endpoints, when using any client in `Neuphonic.agent`."""

    type: str = Field(
        description='Type of message being sent by the server',
        examples=['llm_response', 'audio_response', 'user_transcript'],
    )

    text: Optional[str] = Field(
        default=None,
        description=(
            'Corresponding text if the `type` is `llm_response` or `user_transcript`.'
        ),
    )


class WebsocketEvents(Enum):
    """Enum describing all valid websocket events that callbacks can be bound to."""

    OPEN: str = 'open'
    MESSAGE: str = 'message'
    CLOSE: str = 'close'
    ERROR: str = 'error'


class WebsocketEventHandlers(BaseModel):
    """Pydantic model to hold all websocket callbacks."""

    open: Optional[Callable[[], Awaitable[None]]] = None
    message: Optional[Callable[[APIResponse[T]], Awaitable[None]]] = None
    close: Optional[Callable[[], Awaitable[None]]] = None
    error: Optional[Callable[[Exception], Awaitable[None]]] = None
