import enum


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class InferenceStatus(str, enum.Enum):
    success = "success"
    error = "error"
