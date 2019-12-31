from utils.api import JSONResponse


class BasePermissionDecorator(object):
    def __init__(self, func):
        self.func = func

    def error(self, data):
        return JSONResponse.response({'error': 'permission-denied', 'data': data})

    def check_permission(self):
        return NotImplementedError()

    def __call__(self, *args, **kwargs):
        # 为了能够在check_permission方法中拿到request所以放到类的实例当中.
        self.request = args[1]
        if self.check_permission():
            if self.request.user.is_disabled:
                return self.error('Your account is disabled')
            return self.func(*args, **kwargs)
        return self.error('Please login first')


class login_required(BasePermissionDecorator):
    def check_permission(self):
            return self.request.user.is_authenticated


class super_admin_required(BasePermissionDecorator):
    def check_permission(self):
        user = self.request.user
        return user.is_authenticated and user.is_super_admin()


class admin_role_required(BasePermissionDecorator):
    def check_permission(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_role()
