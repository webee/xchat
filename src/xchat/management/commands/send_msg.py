from django.core.management.base import BaseCommand
from django.conf import settings
from xchat.authentication import decode_ns_user
import requests
import json
from ._utils import gen_token


class Command(BaseCommand):
    help = "test command"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('msg', nargs=1, type=str)

        # Named (optional) arguments
        parser.add_argument('-chat_id', type=str, dest='chat_id', required=True, help='chat id')
        parser.add_argument('-user', type=str, dest='user', required=True, help='the sender')
        parser.add_argument('-kind', type=str, dest='kind', default="chat", help='the msg kind, default is chat msg')
        parser.add_argument('-domain', type=str, dest='domain', default="", help='the domain, default to ignore it')
        parser.add_argument('-perm_check', action='store_true', dest='perm_check', default=False, help='whether to check user permission')

    def handle(self, *args, **options):
        chat_id = options['chat_id']
        ns_user = options['user']
        ns, user = decode_ns_user(ns_user)
        msg = options['msg'][0]

        token = gen_token(user, ns=ns, is_admin=True)

        params = {
            'chat_id': chat_id,
            'user': user,
            'msg': msg,
            'kind': options['kind'],  # can ignore when it's ""/"chat"
            'domain': options['domain'],  # can ignore when it's "".
            'perm_check': options['perm_check']  # can ignore when it's False.

        }
        self.stdout.write(self.style.NOTICE("params:"))
        self.stdout.write(self.style.NOTICE(json.dumps(params, indent=True)))

        headers = {'Authorization': 'Bearer ' + token}
        req = requests.post(settings.XCHAT_API_ROOT_URL + "/xchat/api/user/msg/send/", json=params, headers=headers)
        req.raise_for_status()

        self.stdout.write(self.style.SUCCESS(""))
        self.stdout.write(self.style.SUCCESS("status code: %d" % req.status_code))
        self.stdout.write(self.style.SUCCESS(json.dumps(req.json(), indent=True)))
