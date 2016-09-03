from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "test command"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('s', nargs='*', type=str)

        # Named (optional) arguments
        parser.add_argument('-a', type=int, dest='a', default=0, help='non-negative operand a')
        parser.add_argument('-b', type=int, dest='b', default=0, help='non-negative operand b')

    def handle(self, *args, **options):
        for i, s in enumerate(options['s'], 0):
            self.stdout.write(self.style.SUCCESS("s.%d=%s" % (i, s)))

        a = options['a']
        b = options['b']
        if a < 0 or b < 0:
            raise CommandError("a and b must be non-negative: a = %d, b = %d" % (a, b))
        self.stdout.write(self.style.SUCCESS("a + b = %d" % (a + b)))
