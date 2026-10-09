from pydantic import BaseModel, Field, HttpUrl

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    memories_used: list[dict] = []

class RememberRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50000)
    source_url: HttpUrl | None = None
    source_title: str | None = Field(default=None, max_length=512)

class FileWriteRequest(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    content: str = Field(max_length=100000)

class ApprovalRequest(BaseModel):
    approve: bool
