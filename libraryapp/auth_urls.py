from django.urls import path
from rest_framework_simplejwt import views
from django.views.decorators.cache import never_cache

from libraryapp.views import UserRegisterView

urlpatterns = [
    path('register', never_cache(UserRegisterView.as_view()), name="register"),
    path('login', never_cache(views.TokenObtainPairView.as_view()), name="jwt-create"),
    path('refresh', never_cache(views.TokenRefreshView.as_view()), name="jwt-refresh"),
    path('verify', never_cache(views.TokenVerifyView.as_view()), name="jwt-verify"),
]