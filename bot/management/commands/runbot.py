import logging

from django.core.management.base import BaseCommand
from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal, GoalCategory
from todolist import settings


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.tg_client = TgClient(token=settings.TG_TOKEN)
        self.__tg_user: TgUser | None = None
        self.logger = logging.getLogger(__name__)
        self.logger.info('Bot start pooling')
        self._state = None
        self._category = None

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
                if self.tg_user.user:
                    self._handle_verified_user(item.message)
                else:
                    self._handle_unverified_user(item.message)

    def _handle_unverified_user(self, message: Message):
        verification_code: str = self.tg_user.set_verification_code()
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
            case '/create':
                self._handle_category_list(message)
            case '/cancel':
                self.tg_client.send_message(message.chat.id, 'Операция создания цели отменена.')
                self._state = None
            case _:
                self._handle_message(message)

    def _handle_message(self, message: Message):
        if self._state == 'get_category':
            self._handle_get_category(message)
        elif self._state == 'create_goal':
            self._handle_create_goal(message)
        elif self._state == 'save_category':
            self._handle_save_category(message)
        else:
            self.tg_client.send_message(message.chat.id, f'{message.text} не является командой.')

    def _handle_goals_command(self, message: Message):
        goals: list[str] = list(
            Goal.objects.filter(user_id=self.tg_user.user).exclude(status=Goal.Status.archived).values_list(
                'title',
                flat=True
            )
        )
        self.tg_client.send_message(
            chat_id=message.chat.id,
            text='\nВаши цели:\n' + '\n'.join(goals) if goals else 'Целей не найдено.'
        )
        if not goals:
            self._state = None

    def _handle_category_list(self, message: Message):
        self._state = 'get_category'
        category: list[str] = list(
            GoalCategory.objects.filter(user_id=self.tg_user.user).exclude(is_deleted=True).values_list(
                'title',
                flat=True
            )
        )
        if category:
            self.tg_client.send_message(
                chat_id=message.chat.id,
                text='\nВыберите категорию:\n' + '\n'.join(category) + '\n/cancel - Отмена.'
            )
            self._state = 'save_category'

        else:
            self._state = None
            self.tg_client.send_message(
                chat_id=message.chat.id,
                text='Категории не найдены. Создайте категорию на сайте.'
            )

    def _handle_create_goal(self, message: Message):

        goal = Goal.objects.create(
            title=message.text,
            category=self._category,
            user_id=self.tg_user.user_id,
        )
        self.tg_client.send_message(message.chat.id, f'Цель {goal.title} успешно создана.')
        self._state = None

    def _handle_get_category(self, message):
        categories = list(
            GoalCategory.objects.filter(user_id=self.tg_user.user).exclude(is_deleted=True).values_list('title'))
        cat = list(map(lambda x: x[0], categories))
        if len(cat) == 0:
            self._state = None
        elif len(cat) != 0 and message.text in cat:
            self.tg_client.send_message(message.chat.id, 'Введите название цели.')
            self._state = 'create_goal'
        else:
            self.tg_client.send_message(message.chat.id, 'Неверно выбрана категория.')

    def _handle_save_category(self, message: Message):
        try:
            self._category = GoalCategory.objects.get(title=message.text)
        except GoalCategory.DoesNotExist:
            self._category = None
        self._handle_get_category(message)
