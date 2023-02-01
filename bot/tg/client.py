import requests

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __init__(self, token):
        self.token = token

    def get_url(self, method: str):
        return f'https://api.telegram.org/bot{self.token}/{method}'

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        req = requests.get(self.get_url(method='getUpdates')).json()
        try:
            obj = GetUpdatesResponse(**req, offset=offset, timeout=timeout)
            return obj
        except NotImplementedError:
            raise NotImplementedError

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        req = requests.get(self.get_url(method=f'sendMessage?chat_id={chat_id}&text={text}')).json()
        try:
            obj = SendMessageResponse(**req, chat_id=chat_id, text=text)
            return obj
        except NotImplementedError:
            raise NotImplementedError
