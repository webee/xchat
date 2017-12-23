import arrow
from django.db import transaction, connection
from rest_framework import serializers
from pytoolbox.jwt import encode_ns_user
from .models import Chat, Member, ChatTypes, ChatType
from .ex_models import Message


def decode_chat_id(chat_id):
    parts = chat_id.split('.', 1)
    return parts[0], int(parts[1])


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('user', 'cur_id', 'joined', 'is_exited', 'exit_msg_id', 'dnd')


class ChatSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False, allow_blank=False, source="chat_id")
    type = serializers.CharField(allow_blank=False, max_length=10)
    app_id = serializers.CharField(required=False, allow_blank=False, max_length=16, allow_null=True, default=None)
    biz_id = serializers.CharField(required=False, allow_blank=False, max_length=160, allow_null=True, default=None)
    start_msg_id = serializers.IntegerField(required=False, min_value=0, default=0)
    is_deleted = serializers.ReadOnlyField()
    users = serializers.ListField(required=False, write_only=True,
                                  child=serializers.CharField(allow_blank=False, max_length=100), default=[])

    class Meta:
        model = Chat
        fields = (
        'id', 'biz_id', 'app_id', 'type', 'users', 'title', 'tag', 'start_msg_id', 'ext', 'is_deleted', 'created')

    def validate_type(self, value):
        if value not in ChatTypes:
            raise serializers.ValidationError("invalid chat type")
        return value

    def validate_users(self, value):
        if len(value) <= 0:
            return []
        user = value[0]
        users = set(value)
        users.remove(user)
        return [user] + list(users)

    def validate(self, data):
        t = data['type']
        if t == ChatType.SELF and len(data['users']) != 1:
            raise serializers.ValidationError("self chat must have and only have one member")
        if t == ChatType.USER and len(data['users']) != 2:
            if len(data['users']) == 1:
                data['type'] = ChatType.SELF
            else:
                raise serializers.ValidationError("user chat must have and only have two members")
        if t == ChatType.USERS:
            if len(data['users']) < 2:
                raise serializers.ValidationError("users chat must have more than 1 members")
            elif len(data['users']) >= 100:
                raise serializers.ValidationError("users chat must have less than 100 members")
        if t == ChatType.CS and len(data['users']) != 1:
            raise serializers.ValidationError("cs chat must have and only have one member")
        if t not in [ChatType.SELF, ChatType.USER, ChatType.USERS] and data.get('tag') == "user":
            raise serializers.ValidationError("tag 'user' is reserved for user created chats")

        return data

    @transaction.atomic
    def create(self, validated_data):
        ns = validated_data['ns']
        t = validated_data['type']
        users = [encode_ns_user(ns, user) for user in validated_data['users']]
        chat_id = validated_data.get('chat_id')
        id = None
        if chat_id:
            # 指定chat_id, 则优先使用这里的t
            t, id = decode_chat_id(chat_id)

        key = None
        owner = None
        tag = validated_data.get('tag')
        if t == ChatType.SELF:
            # 用户建会话
            tag = 'user'
            owner = users[0]
            # 自聊唯一
            key = owner
        elif t == ChatType.USER:
            # 用户建会话
            tag = 'user'
            # 创建者
            owner = users[0]
            # 单聊唯一
            key = ','.join(sorted(users))
        elif t == ChatType.USERS:
            # 用户建会话
            tag = 'user'
            # 创建者
            owner = users[0]
        elif t == ChatType.CS:
            # TODO: 客服通过tag区别不同的客服团队
            tag = '_cs'
            owner = users[0]
            # 同一tag的user客服唯一
            key = '%s|%s' % (tag, owner)

        app_id = validated_data.get('app_id')
        start_msg_id = validated_data.get('start_msg_id')
        title = validated_data.get('title')
        ext = validated_data.get('ext')
        chat = None
        if id:
            chat = Chat.objects.filter(id=id, type=t).first()
        elif t in [ChatType.SELF, ChatType.USER, ChatType.CS]:
            chat = Chat.objects.filter(type=t, key=key).first()

        biz_id = validated_data.get('biz_id')
        if t != ChatType.GROUP:
            biz_id = None

        if not chat and biz_id:
            # biz id唯一
            chat = Chat.objects.filter(biz_id=biz_id).first()

        if chat is not None:
            updated_fields = set_update_chat(chat, biz_id, app_id, title, tag, ext, is_deleted=False)
            # update
            if updated_fields:
                chat.update_updated(fields=updated_fields)
        else:
            chat = Chat(type=t, key=key, biz_id=biz_id, owner=owner, start_msg_id=start_msg_id, msg_id=start_msg_id)
            set_update_chat(chat, biz_id, app_id, title, tag, ext)
            chat.save()

        update_chat_members(chat, users)
        return chat


def set_update_chat(chat, biz_id=None, app_id=None, title=None, tag=None, ext=None, is_deleted=None):
    updated = []
    if biz_id is not None and biz_id != chat.biz_id:
        updated.append('biz_id')
        chat.biz_id = biz_id
    if app_id is not None and app_id != chat.app_id:
        updated.append('app_id')
        chat.app_id = app_id
    if title is not None and title != chat.title:
        updated.append('title')
        chat.title = title
    if tag is not None and tag != chat.tag:
        updated.append('tag')
        chat.tag = tag
    if ext is not None and ext != chat.ext:
        updated.append('ext')
        chat.ext = ext
    if is_deleted is not None and is_deleted != chat.is_deleted:
        updated.append('is_deleted')
        chat.is_deleted = is_deleted

    return updated


class MembersSerializer(serializers.Serializer):
    users = serializers.ListField(required=False, child=serializers.CharField(allow_blank=False, max_length=100),
                                  default=[])

    def update(self, instance, validated_data):
        return self.create(validated_data)

    @transaction.atomic
    def create(self, validated_data):
        ns = validated_data['ns']
        chat = validated_data['chat']
        users = [encode_ns_user(ns, user) for user in validated_data['users']]

        chat_update_users(chat, users)
        return True


def chat_update_users(chat, users):
    do_updated = False
    for user in users:
        do_updated = get_or_create_member(chat, user)

    # update
    if do_updated:
        chat.update_members_updated()


def get_or_create_member(chat, user):
    member, created = Member.objects.get_or_create(chat=chat, user=user)
    if created or member.is_exited:
        member.cur_id = chat.msg_id
        member.join_msg_id = chat.msg_id
        member.is_exited = False
        member.dnd = False
        member.save()
        return True


@transaction.atomic
def update_chat_members(chat, new_users):
    old_users = [m.user for m in chat.members.all()]

    to_delete_users = list(set(old_users) - set(new_users))
    to_add_users = list(set(new_users) - set(old_users))

    do_updated = False
    if len(to_delete_users) > 0:
        do_updated = True
        chat.members.filter(user__in=to_delete_users).delete()

    if len(to_add_users) > 0:
        do_updated = True
        for user in to_add_users:
            get_or_create_member(chat, user)

    if do_updated:
        chat.update_members_updated()


class MessageSerializer(serializers.ModelSerializer):
    ts = serializers.FloatField()
    domain = serializers.CharField(required=False, max_length=16, default='')

    class Meta:
        model = Message
        fields = ('uid', 'msg', 'ts', 'domain')


class MessagesSerializer(serializers.Serializer):
    msgs = serializers.ListField(required=False, child=MessageSerializer(), default=[])

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def create(self, validated_data):
        ns = validated_data['ns']
        chat = validated_data['chat']

        msgs = [dict(uid=encode_ns_user(ns, msg.get('uid')),
                     ts=arrow.get(msg.get('ts')).datetime,
                     msg=msg.get('msg'),
                     domain=msg.get('domain')) for msg in validated_data['msgs']]

        if len(msgs) <= 0:
            return 0

        return chat_insert_msgs(chat, msgs)


@transaction.atomic
def chat_insert_msgs(chat, msgs):
    chat = Chat.objects.select_for_update().get(pk=chat.id)
    n = 0
    with connection.cursor() as cursor:
        for msg in msgs:
            if chat.start_msg_id <= 0:
                break
            cursor.execute(
                'INSERT INTO xchat_message(chat_id, chat_type, id, uid, ts, msg, domain) VALUES(%S, %S, %S, %S, %S, %S, %S)',
                [chat.id, chat.type, chat.start_msg_id, msg['uid'], msg['ts'], msg['msg'], msg['domain']])
            chat.start_msg_id -= 1
            n += 1
    chat.update_updated(fields=['start_msg_id'])

    return n
