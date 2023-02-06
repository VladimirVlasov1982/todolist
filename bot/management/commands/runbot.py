import logging

from django.core.management.base import BaseCommand
from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal
from todolist import settings


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.tg_client = TgClient(token=settings.TG_TOKEN)
        self.__tg_user: TgUser | None = None
        self.logger = logging.getLogger(__name__)
        self.logger.info('Bot start pooling')

    @property
    def tg_user(self) -> TgUser:
        if self.__tg_user:
            return self.__tg_user
        raise RuntimeError('Пользователь не существует')

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.__tg_user, _ = TgUser.objects.get_or_create(
                    chat_id=item.message.chat.id,
                    defaults={'username': item.message.from_.username}
                )
                if self.tg_user.user_id:
                    self._handle_verified_user(item.message)
                else:
                    self._handle_unverified_user(item.message)

    def _handle_unverified_user(self, message: Message):
        verification_code: str = self.tg_user.verification_code
        self.tg_client.send_message(
            chat_id=message.chat.id,
            text=f'Подтвердите, пожалуйста, свой аккаунт. '
                 f'Для подтверждения необходимо ввести код: {verification_code} на сайте'
        )

    def _handle_verified_user(self, message: Message):
        self.logger.info('User verified')
        if message.text.startswith('/'):
            self._handle_command(message)
        else:
            self._handle_message(message)

    def _handle_command(self, message: Message):
        match message.text:
            case '/goals':
                self._handle_goals_command(message)
            case _:
                self._handle_message(message)

    def _handle_message(self, message: Message):
        if message.text != '/goals':
            self.tg_client.send_message(message.chat.id, 'Неизвестная команда')

        self.logger.info(f'Пользователь отправил: {message.text}')

    def _handle_goals_command(self, message: Message):
        goals: list[str] = list(
            Goal.objects.filter(user_id=self.tg_user.user).exclude(status=Goal.Status.archived).values_list(
                'title',
                flat=True
            )
        )
        self.tg_client.send_message(
            chat_id=message.chat.id,
            text='\n'.join(goals) if goals else 'Целей не найдено'
        )
