from pydantic import BaseModel as BaseModel, field_validator
from typing import List, Literal, Optional
import base64


def to_dict(model: BaseModel):
    """Returns a pydantic model as dict, with all of the None items removed."""
    return {k: v for k, v in model.model_dump().items() if v is not None}


class VoiceData(BaseModel):
    id: str
    name: str
    tags: List[str]


class TTSConfig(BaseModel):
    speed: float = 1.0
    temperature: float = 0.5
    model: Literal['neu_fast', 'neu_hq'] = 'neu_fast'
    voice: str | None = None
    sampling_rate: Literal[22050, 8000] = 22050
    encoding: Literal['pcm_linear', 'pcm_mulaw'] = 'pcm_linear'
    language_id: Literal['en'] = 'en'


class SSEResponse(BaseModel):
    class Data(BaseModel):
        audio: bytes
        text: str
        sampling_rate: Optional[int] = None

        @field_validator('audio', mode='before')
        def validate(cls, v: str | bytes) -> bytes:
            if isinstance(v, str):
                return base64.b64decode(v)
            elif isinstance(v, bytes):
                return v

            raise ValueError('`audio` must be a base64 encoded string or bytes.')

    status_code: int
    data: Data


class SSERequest(BaseModel):
    text: str
    model: TTSConfig
