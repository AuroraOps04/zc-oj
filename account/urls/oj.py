from django.conf.urls import url

from ..views.oj import (
    UserRegisterAPIView, UserLoginAPIView,
)
from utils.captcha.views import CaptchaAPIView

urlpatterns = [
    url(r'^register$', UserRegisterAPIView.as_view(), name='user_register_api'),
    url(r'^login$', UserLoginAPIView.as_view(), name='user_login_api'),
    url(r'^captcha$', CaptchaAPIView.as_view(), name='show_captcha')
]