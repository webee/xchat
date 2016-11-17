from django.conf import settings
from django.db.models import Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
import time
import pytz
import datetime
from .ex_models import Message


DATE_FORMAT = '%Y-%m-%d'


def check_date_format(dt):
    try:
        _ = datetime.datetime.strptime(dt, DATE_FORMAT)
        return True
    except:
        return False


def get_yesterday():
    y = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)) - datetime.timedelta(days=1)
    return y.strftime(DATE_FORMAT)


def parse_chat_ids(chat_ids):
    return [int(i.split('.')[1]) for i in chat_ids.split(',') if i]


class StatChatUserMsgsView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        st = time.time()

        q = request.query_params
        dt = q.get('dt')
        if dt is None or not check_date_format(dt):
            dt = get_yesterday()

        try:
            chat_ids = parse_chat_ids(q.get('chat_ids', ""))
        except:
            return Response({'ok': False, 'err': "bad chat_ids", 't': 1000 * (time.time() - st)}, status=status.HTTP_400_BAD_REQUEST)

        res = Message.objects.filter(chat_type='group', chat_id__in=chat_ids, ts__date=dt).values("chat_id", "uid").annotate(count=Count("*")).all()
        data = {}
        for r in res:
            d = data.setdefault("%s.%s" % ('group', r['chat_id']), {})
            d[r['uid']] = r['count']
        return Response({'ok': True, 'dt': dt, 'data': data, 't': 1000 * (time.time() - st)})
