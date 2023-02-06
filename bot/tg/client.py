import logging

import requests
from bot.tg.dc import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __init__(self, token: str):
        self.token = token

    def get_url(self, method: str):
        return f'https://api.telegram.org/bot{self.token}/{method}'

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        url = self.get_url('getUpdates')
        try:
            response = requests.get(url, params={'offset': offset, 'timeout': timeout})
        except Exception:
            logging.error('Не удалось получить обновления из Telegram')
            raise ...
        else:
            return GetUpdatesResponse(**response.json())

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url('sendMessage')
        try:
            response = requests.post(url, json={
                'chat_id': chat_id,
                'text': text,
            })
        except Exception:
            logging.error('Не удалось отправить сообщение в Telegram')
            raise ...
        else:
            return SendMessageResponse(**response.json())
