from django.urls import path
from core.views import ProfileView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile')
]
