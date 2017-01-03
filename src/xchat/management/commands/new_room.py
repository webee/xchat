from django.core.management.base import BaseCommand
from django.db import transaction
from xchat.models import Room, Chat, ChatType, RoomChat


class Command(BaseCommand):
    help = "create a room"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('-title', type=str, dest='title', required=True, help='room title')
        parser.add_argument('-tag', type=str, dest='tag', required=True, help='room tag')
        parser.add_argument('-area_count', type=int, dest='area_count', required=False, default=20, help='area count')

    @transaction.atomic
    def handle(self, *args, **options):
        title = options['title']
        tag = options['tag']
        area_count = options['area_count']

        room = Room(title=title, tag=tag)
        room.save()

        chat_title = 'room#%d' % room.id
        self.stdout.write(self.style.SUCCESS(""))
        self.stdout.write(self.style.SUCCESS("room: %d" % room.id))

        for i in range(0, area_count):
            chat = Chat.objects.create(type=ChatType.ROOM, title=chat_title, tag='_room')
            try:
                _ = RoomChat.objects.create(room=room, area=i, chat=chat)
                self.stdout.write(self.style.SUCCESS("area: %d" % i))
            except:
                chat.delete()
