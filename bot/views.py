from rest_framework import generics, permissions
from rest_framework.response import Response

from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient
from todolist import settings


class VerificationView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TgUserSerializer

    def update(self, request, *args, **kwargs):
        serializer: TgUserSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        tg_user = serializer.save()
        TgClient(settings.TG_TOKEN).send_message(
            chat_id=tg_user.chat_id,
            text='Проверка успешно завершена',
        )
