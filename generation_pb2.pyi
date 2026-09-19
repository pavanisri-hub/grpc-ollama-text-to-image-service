from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GenerateImageRequest(_message.Message):
    __slots__ = ("request_id", "prompt")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    prompt: str
    def __init__(self, request_id: _Optional[str] = ..., prompt: _Optional[str] = ...) -> None: ...

class GenerateImageResponse(_message.Message):
    __slots__ = ("request_id", "message", "image_path")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_PATH_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    message: str
    image_path: str
    def __init__(self, request_id: _Optional[str] = ..., message: _Optional[str] = ..., image_path: _Optional[str] = ...) -> None: ...
