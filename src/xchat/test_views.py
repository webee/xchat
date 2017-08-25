from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http.response import JsonResponse
import time
import json
from .models import Chat


def test(request):
    params = request.GET
    res = {'st': time.time()}
    status_code = int(params.get("status", 200))
    sleep = params.get("sleep")
    if sleep:
        time.sleep(float(sleep))

    ok = params.get("not_ok") is None or not params.get("not_ok") == "false"

    res['ok'] = ok
    if not ok:
        code = params.get("code")
        error = params.get("error")
        if code is not None:
            res["code"] = int(code)
        if error is not None:
            res["error"] = error
    else:
        data = params.get("data")
        if data is not None:
            try:
                res["data"] = json.loads(data)
            except json.JSONDecodeError:
                res["data"] = data

    res['et'] = time.time()
    return JsonResponse(res, status=status_code)


def db(request):
    res = {'st': time.time()}

    chat = Chat.objects.get(pk=1)
    time.sleep(float(0.01))

    res['x'] = chat.msg_id
    res['et'] = time.time()
    res['ok'] = True
    return JsonResponse(res, status=status.HTTP_200_OK)


class TestView(APIView):
    permission_classes = ()

    def get(self, request):
        return Response({'ok': True, 't': time.time()})


