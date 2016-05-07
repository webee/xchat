from django.db import models
from django.utils.translation import ugettext_lazy as _


ChatTypes = [
    ("user", "单聊"),
    ("group", "群聊"),
    ("room", "房间"),
]


class Chat(models.Model):
    type = models.CharField(max_length=10, choices=ChatTypes)
    channel = models.CharField(max_length=8, unique=True, null=False, blank=False)
    title = models.CharField(max_length=64, null=True, blank=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")

    def __str__(self):
        return "%s:%s:%s" % (self.type, self.channel, self.title)


class Member(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='members')

    user = models.CharField(max_length=32, null=False, blank=False)
