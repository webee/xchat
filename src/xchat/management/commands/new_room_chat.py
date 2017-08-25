from django.core.management.base import BaseCommand
from django.db import transaction
from xchat.models import Room, Chat, ChatType, RoomChat


class Command(BaseCommand):
    help = "create chats for room"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('-room_id', type=int, dest='room_id', required=True, help='room id')
        parser.add_argument('-count', type=int, dest='count', required=True, help='the sender')

    @transaction.atomic
    def handle(self, *args, **options):
        room_id = options['room_id']
        count = options['count']

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            self.stderr.write("room #%d not exists" % room_id)
            return
        max_area = room.max_area()
        chat_title = 'room#%d' % room.id

        self.stdout.write(self.style.SUCCESS(""))
        for i in range(max_area + 1, max_area + 1 + count):
            chat = Chat.objects.create(type=ChatType.ROOM, title=chat_title, tag='_room')
            try:
                _ = RoomChat.objects.create(room=room, area=i, chat=chat)
                self.stdout.write(self.style.SUCCESS("area: %d" % i))
            except:
                chat.delete()
