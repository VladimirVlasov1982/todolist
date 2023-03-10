from pydantic import BaseModel, Field


class MessageFrom(BaseModel):
    id: int
    username: str | None = None


class Chat(BaseModel):
    id: int
    username: str | None = None


class Message(BaseModel):
    message_id: int
    from_: MessageFrom = Field(..., alias='from')
    chat: Chat
    text: str | None = None

    class Config:
        allow_population_by_field_name = True


class UpdateOdj(BaseModel):
    update_id: int
    message: Message


class GetUpdatesResponse(BaseModel):
    ok: bool
    result: list[UpdateOdj] = []


class SendMessageResponse(BaseModel):
    ok: bool
    result: Message
