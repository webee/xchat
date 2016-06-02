from django.db import models
from django.utils.translation import ugettext_lazy as _


class ChatType:
    SELF = "self"
    USER = "user"
    GROUP = "group"

ChatTypeChoices = [
    (ChatType.SELF, "自聊"),
    (ChatType.USER, "单聊"),
    (ChatType.GROUP, "群聊"),
]

ChatTypes = {c[0] for c in ChatTypeChoices}


class Chat(models.Model):
    type = models.CharField(max_length=10, choices=ChatTypeChoices)
    title = models.CharField(max_length=64, null=True, default="", blank=True)
    tag = models.CharField(max_length=8, null=False, default="", db_index=True, blank=True)
    msg_id = models.BigIntegerField(default=0)

    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")

    def __str__(self):
        return "%s:#%d" % (self.type, self.id)


class Member(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="members")
    user = models.CharField(max_length=32, null=False, db_index=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    init_id = models.BigIntegerField(default=0)
    cur_id = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Member")

        unique_together = (('chat', 'user'),)

    def __str__(self):
        return "%s@%s" % (self.user, self.chat)
