from django.db import models


class ReadOnlyManager(models.Manager):
    # TODO:
    pass


class Message(models.Model):
    chat_id = models.BigIntegerField()
    chat_type = models.CharField(max_length=10)
    id = models.BigIntegerField()
    uid = models.CharField(max_length=32)
    ts = models.DateTimeField()
    msg = models.TextField()
    domain = models.CharField(max_length=16)

    objects = ReadOnlyManager()

    class Meta:
        managed = False

    def __str__(self):
        return "(%d.%s,%s)%s:#%d@[%s]" % (self.chat_id, self.chat_type, self.domain, self.uid, self.id, self.ts)

    def save(self, *args, **kwargs):
        raise Exception("ReadOnly")

    def delete(self, *args, **kwargs):
        raise Exception("ReadOnly")
