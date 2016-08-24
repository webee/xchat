from django.db import models
from django.utils.translation import ugettext_lazy as _


class ChatType:
    SELF = "self"
    USER = "user"
    USERS = "users"
    GROUP = "group"
    CS = "cs"
    ROOM = "room"


ChatTypeChoices = [
    (ChatType.SELF, "自聊"),
    (ChatType.USER, "单聊"),
    (ChatType.USERS, "讨论组"),
    (ChatType.GROUP, "群组"),
    (ChatType.CS, "客服"),
    (ChatType.ROOM, "房间")
]

ChatTypes = {c[0] for c in ChatTypeChoices}


class Room(models.Model):
    title = models.CharField(max_length=64, null=True, default="", blank=True)
    tag = models.CharField(max_length=8, null=False, default="", db_index=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")

    def __str__(self):
        return "#%d:%s" % (self.id, self.title)


class Chat(models.Model):
    type = models.CharField(max_length=10, choices=ChatTypeChoices)
    title = models.CharField(max_length=64, null=True, default="", blank=True)
    tag = models.CharField(max_length=8, null=False, default="", db_index=True, blank=True)
    msg_id = models.BigIntegerField(default=0)
    ext = models.TextField(default="", blank=True)

    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    # 添加成员之后需要更新这里
    updated = models.DateTimeField(auto_now=True, editable=False)

    def update_updated(self, fields=None):
        self.save(update_fields=['updated'] + (fields if fields else []))

    @property
    def chat_id(self):
        return "%s.%d" % (self.type, self.id)

    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")

    def __str__(self):
        return "%s#%d@%s" % (self.type, self.id, self.tag)


class RoomChat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="chats", null=True, editable=False)
    area = models.IntegerField(default=0)
    chat = models.OneToOneField(Chat)

    class Meta:
        verbose_name = _("RoomChat")
        verbose_name_plural = _("RoomChats")

        unique_together = (("room", "area"),)

    def __str__(self):
        return "%s#%d#%s" % (self.room, self.area, self.chat)


class Member(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="members")
    user = models.CharField(max_length=32, null=False, db_index=True)

    joined = models.DateTimeField(auto_now_add=True, editable=False)
    cur_id = models.BigIntegerField(default=0)
    exit_msg_id = models.BigIntegerField(default=0)
    is_exited = models.BooleanField(default=False)
    # Do Not Disturb
    dnd = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")

        unique_together = (('chat', 'user'),)

    def __str__(self):
        return "%s@%s" % (self.user, self.chat)
