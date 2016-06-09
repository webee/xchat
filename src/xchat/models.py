from django.db import models
from django.utils.translation import ugettext_lazy as _


class ChatType:
    SELF = "self"
    USER = "user"
    GROUP = "group"
    CS = "cs"

ChatTypeChoices = [
    (ChatType.SELF, "自聊"),
    (ChatType.USER, "单聊"),
    (ChatType.GROUP, "群聊"),
    (ChatType.CS, "客服"),
]

ChatTypes = {c[0] for c in ChatTypeChoices}


class Room(models.Model):
    title = models.CharField(max_length=64, null=True, default="", blank=True)
    tag = models.CharField(max_length=8, null=False, default="", db_index=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)


class Chat(models.Model):
    type = models.CharField(max_length=10, choices=ChatTypeChoices)
    title = models.CharField(max_length=64, null=True, default="", blank=True)
    tag = models.CharField(max_length=8, null=False, default="", db_index=True, blank=True)
    msg_id = models.BigIntegerField(default=0)

    # 所属房间, 可以为null表示为系统房间
    # 房间中可以有 self, user, group, cs等会话,
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="chats", null=True)

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

    joined = models.DateTimeField(auto_now_add=True, editable=False)
    cur_id = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")

        unique_together = (('chat', 'user'),)

    def __str__(self):
        return "%s@%s" % (self.user, self.chat)


class DeviceInfo(models.Model):
    """ 记录用户设备信息, 作进一步处理(离线消息推送等)
    """
    user = models.CharField(max_length=32, null=False, db_index=True)
    dev = models.CharField(max_length=32, null=False)
    dev_id = models.CharField(max_length=256, null=False)
    info = models.TextField()

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Device info")
        verbose_name_plural = _("Device infos")

        unique_together = (('user', 'dev', 'dev_id'),)

    def __str__(self):
        return "%s@%s" % (self.user, self.dev_id)
