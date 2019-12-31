from . import Captcha
from ..api import APIView
from ..shortcuts import img2base64


class CaptchaAPIView(APIView):
    def get(self, request):
        print(request.COOKIES)
        resp = self.success(img2base64(Captcha(request).get()))
        resp.set_cookie('my_cookie', 'saf')
        return resp
