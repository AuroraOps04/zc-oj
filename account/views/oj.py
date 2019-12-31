
from django.contrib.auth import authenticate, login

from utils.api import APIView, CSRFExemptAPIView
from ..models import User
from utils.captcha import Captcha
from utils.api import validate_serializer
from ..serializers import (
    UserRegisterSerializer, UserLoginSerializer,
)


class UserRegisterAPIView(APIView):

    @validate_serializer(UserRegisterSerializer)
    def post(self, request):

        data = request.data
        # 判断验证码是否正确
        captcha = Captcha(request)
        if not captcha.check(data.get('captcha')):
            return self.error("Invalid captcha")

        # 判断用户名和邮箱是否存在
        # 用户名和邮箱都保存小写
        data['username'] = data['username'].lower()
        data['email'] = request.data['email'].lower()
        if User.objects.filter(username=data.get('username')).exists():
            return self.error(msg="Username already exists")
        if User.objects.filter(username=data.get('email')).exists():
            return self.error(msg="Email already exists")

        # 创建用户

        user = User.objects.create(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        user.save()

        # UserProfile.objects.create(user=user)

        res = self.success("Succeeded")
        return res


class UserLoginAPIView(APIView):
    @validate_serializer(UserLoginSerializer)
    def post(self, request):
        # 验证用户名密码是否正确
        user = authenticate(request, username=request.data.get('username'), password=request.data.get('password'))
        if user:
            login(request, user)
            if user.is_disabled:
                return self.error("Your account is disabled")
            return self.success("Succeeded")
        else:
            return self.error('Invalid account or password')

