from django.db import models
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _
from django.utils.datetime_safe import datetime


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


class App(models.Model):
    app_id = models.CharField(max_length=16, null=False, unique=True)
    # 消息通知url
    msg_notify_url = models.CharField(max_length=128, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = _("App")
        verbose_name_plural = _("Apps")

    def __str__(self):
        return "<App: %s>" % (self.app_id,)


class Room(models.Model):
    title = models.CharField(max_length=64, null=True, default="", blank=True)
    tag = models.CharField(max_length=8, null=False, default="", db_index=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")

    def max_area(self):
        res = self.chats.aggregate(Max('area'))
        if res:
            area_max = res['area__max']
            return area_max if area_max is not None else -1
        return -1

    def __str__(self):
        return "#%d:%s" % (self.id, self.title)


class Chat(models.Model):
    type = models.CharField(max_length=10, choices=ChatTypeChoices)
    # self -> '<owner>'
    # cs -> '<tag>|<owner>'
    # user -> '<user1>,<user2>', user1 < user2
    key = models.CharField(max_length=100, null=True, unique=True, editable=False)

    # biz id
    app_id = models.CharField(max_length=16, null=True, blank=True)
    biz_id = models.CharField(max_length=160, null=True, unique=True, blank=True)

    title = models.CharField(max_length=64, null=False, default="", blank=True)
    tag = models.CharField(max_length=8, null=False, default="", db_index=True, blank=True)
    # 最后消息id, 消息id是针对每个会话的
    msg_id = models.BigIntegerField(editable=False, default=0)
    # 最后消息时间, 针对所有会话, 检查是否有更新
    last_msg_ts = models.DateTimeField(editable=False, default=datetime(1970, 1, 1))
    ext = models.TextField(default="", blank=True)

    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    # 添加成员之后需要更新这里
    members_updated = models.DateTimeField(auto_now=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    # 所有者
    owner = models.CharField(max_length=32, null=True, default=None, db_index=True, blank=True)

    def update_updated(self, fields=None):
        self.save(update_fields=['updated'] + (fields if fields else []))

    def update_members_updated(self, fields=None):
        self.save(update_fields=['updated', 'members_updated'] + (fields if fields else []))

    # only for migration.
    def set_key(self):
        if self.key is None:
            if self.type == ChatType.SELF:
                self.key = self.owner
                self.save()
            elif self.type == ChatType.USER:
                users = [m.user for m in self.members.all()]
                self.key = ','.join(sorted(users))
                self.save()
            elif self.type == ChatType.CS:
                self.key = '%s|%s' % (self.tag, self.owner)
                self.save()

    @property
    def chat_id(self):
        return "%s.%d" % (self.type, self.id)

    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")

        unique_together = (("type", "key"),)

    def save(self, *args, **kwargs):
        if not self.biz_id:
            self.biz_id = None
        super(Chat, self).save(*args, **kwargs)

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
    user = models.CharField(max_length=100, null=False, db_index=True)

    joined = models.DateTimeField(auto_now_add=True, editable=False)
    # 加入时的消息id
    join_msg_id = models.BigIntegerField(default=0, editable=False)
    # 当前同步的消息id
    cur_id = models.BigIntegerField(default=0, editable=False)
    # 离开时的消息id
    exit_msg_id = models.BigIntegerField(default=0, editable=False)
    is_exited = models.BooleanField(default=False)
    # Do Not Disturb
    dnd = models.BooleanField(default=False)
    label = models.TextField(default="", blank=True)

    # 修改成员信息时需要更新这里
    updated = models.DateTimeField(auto_now=True, editable=False)

    def update_updated(self, fields=None):
        self.save(update_fields=['updated'] + (fields if fields else []))

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")

        unique_together = (('chat', 'user'),)

    def __str__(self):
        return "%s@%s" % (self.user, self.chat)
