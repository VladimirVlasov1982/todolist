from django.urls import path
from core.views import ProfileView, SignupView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('signup/', SignupView.as_view(), name='signup'),
]
