import json
import logging
from functools import wraps

from django.http import QueryDict, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger('')


class ContentType(object):
    request_json = 'application/json'
    response_json = 'application/json;charset=utf8'
    request_url_encoded = 'application/x-www-form-urlencoded'
    response_binary = 'application/octet-steam'


class APIError(Exception):
    def __init__(self, msg, err=None):
        self.msg = msg
        self.err = err or ""


class JsonParser(object):
    content_type = ContentType.request_json

    @staticmethod
    def parse(body):
        return json.loads(body.decode('utf-8').replace('\'', '\"'))


class UrlEncodeParser(object):
    content_type = ContentType.request_url_encoded

    @staticmethod
    def parse(body):
        return QueryDict(body)


class JSONResponse(object):
    content_type = ContentType.response_json

    @classmethod
    def response(cls, data):
        resp = HttpResponse(json.dumps(data, indent=4), content_type=cls.content_type)
        resp.data = data
        return resp


class APIView(View):
    request_parsers = [JsonParser, UrlEncodeParser]
    response_class = JSONResponse

    def _get_request_data(self, request):
        if request.method not in ['GET', 'DELETE']:
            body = request.body
            content_type = request.META.get('CONTENT_TYPE')
            if not content_type:
                raise ValueError('content_type is required')
            for parser in self.request_parsers:
                if content_type.startswith(parser.content_type):
                    break
            else:
                raise ValueError('unknown content_type %s' % content_type)
            return parser.parse(body)
        return request.GET

    def response(self, data):
        return self.response_class.response(data=data)

    def success(self, msg):
        return self.response({'error': '', 'data': msg})

    def error(self, msg='error', err='error'):
        return self.response({'error': err, 'data': msg})

    def server_error(self):
        return self.error(msg='server error', err='server-error')

    def extract_errors(self, errors, key='field'):
        if isinstance(errors, dict):
            if not errors:
                return key, 'Invalid field'
            key = list(errors.keys())[0]
            return key, self.extract_errors(errors.pop(key), key)
        if isinstance(errors, list):
            return key, self.error(errors[0], key)

        return key, errors

    def Invalid_serializer(self, serializer):
        key, error = self.extract_errors(serializer.errors)
        if key == "non_field_errors":
            msg = error
        else:
            msg = f"{key}: {error}"
        return self.error(err=f"invalid-{key}", msg=msg)

    def paginate_data(self, request, query_set, object_serializer=None):
        try:
            limit = int(request.GET.get('limit', '10'))
        except ValueError:
            limit = 10
        if limit < 0 or limit > 350:
            limit = 10

        try:
            offset = int(request.GET.get('offset', '0'))
        except ValueError:
            offset = 0
        if offset < 0:
            offset = 0

        results = query_set[offset: offset + limit]

        count = query_set.count()
        if object_serializer:
            results = object_serializer(results, many=True).data
        data = {
            'results': results,
            'total': count,
        }
        return data

    def dispatch(self, request, *args, **kwargs):
        if self.request_parsers:
            try:
                request.data = self._get_request_data(request)
            except ValueError as e:
                return self.error(err='invalid-request', msg=str(e))
            return super(APIView, self).dispatch(request, *args, **kwargs)
        # try:
        #     return super(APIView, self).dispatch(request, *args, **kwargs)
        # except APIError as e:
        #     ret = {'msg': e.msg}
        #     if e.err:
        #         ret['err'] = e.err
        #     return self.error(**ret)
        # except Exception as e:
        #     logger.info(e)
        #     return self.server_error()


class CSRFExemptAPIView(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CSRFExemptAPIView, self).dispatch(request, *args, **kwargs)


def validate_serializer(serializer):
    def validate(view_method):
        @wraps(view_method)
        def handle(*args, **kwargs):
            self = args[0]
            request = args[1]
            s = serializer(data=request.data)
            if s.is_valid():
                request.data = s.data
                request.serializer = s
                return view_method(*args, **kwargs)
            else:
                return self.Invalid_serializer(s)
        return handle

    return validate




