from pydantic import BaseModel, Field


class TicketHistoryEntry(BaseModel):
    role: str
    text: str


class CreateTicketRequest(BaseModel):
    apiKey: str
    message: str = Field(min_length=1, max_length=2000)
    category: str | None = None
    priority: str | None = None
    urgency: str | None = None
    chatHistory: list[TicketHistoryEntry] | None = None
