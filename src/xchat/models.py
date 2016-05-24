from django.db import models
from django.utils.translation import ugettext_lazy as _


class ChatType:
    SELF = "self"
    USER = "user"
    GROUP = "group"
    ROOM = "room"

ChatTypeChoices = [
    (ChatType.SELF, "自聊"),
    (ChatType.USER, "单聊"),
    (ChatType.GROUP, "群聊"),
    (ChatType.ROOM, "房间"),
]

ChatTypes = {c[0] for c in ChatTypeChoices}


class User(models.Model):
    user = models.CharField(max_length=32, null=False, unique=True)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.user


class Chat(models.Model):
    type = models.CharField(max_length=10, choices=ChatTypeChoices)
    channel = models.CharField(max_length=8, unique=True, null=False)
    title = models.CharField(max_length=64, null=True, default="", blank=True)
    owner = models.CharField(max_length=32, null=True, blank=True)
    tag = models.CharField(max_length=8, null=False, default="", db_index=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    members = models.ManyToManyField(User, through='Member', related_name="chats")

    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")

    def __str__(self):
        return "%s:%s" % (self.type, self.channel)


class Member(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    init_id = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Member")

        unique_together = (('chat', 'user'),)

    def __str__(self):
        return "%s@%s" % (self.user, self.chat)
