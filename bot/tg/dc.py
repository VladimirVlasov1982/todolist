from pydantic import BaseModel


class Message(BaseModel):
    ...


class UpdateOdj(BaseModel):
    ...


class Chat(BaseModel):
    ...


class MessageFrom(BaseModel):
    ...


class GetUpdatesResponse(BaseModel):
    ok: bool
    result: list[UpdateOdj] = []


class SendMessageResponse(BaseModel):
    ok: bool
    result: Message
