from django.core.management.base import BaseCommand
from datetime import timedelta
from pytoolbox.jwt import decode_ns_user
from ._utils import gen_token


class Command(BaseCommand):
    help = "new token command"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('user', nargs='*', type=str)

        # Named (optional) arguments
        parser.add_argument('-t', type=int, dest='t', default=600, help='timeout minutes')
        parser.add_argument('-ns', type=str, dest='ns', default='', help='ns')
        parser.add_argument('-is-admin', action='store_true', dest='is_admin', default=False, help='whether is admin')

    def handle(self, *args, **options):
        t = options['t']
        is_admin = options['is_admin']
        if is_admin:
            ns = options['ns']
            self.stdout.write(self.style.SUCCESS('%s' % (gen_token(None, ns, timedelta(minutes=t), is_admin))))
        else:
            for ns_user in options['user']:
                ns, user = decode_ns_user(ns_user)
                self.stdout.write(self.style.SUCCESS('%s: %s' % (ns_user, gen_token(user, ns, timedelta(minutes=t)))))
