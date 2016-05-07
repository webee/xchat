from django.conf import settings
import jwt
from django.db import transaction
import datetime
from django.db import IntegrityError
from rest_framework import serializers
import string
from utils import strings
from .models import Chat, Member, ChatTypes


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('user',)


class ChatSerializer(serializers.ModelSerializer):
    channel = serializers.ReadOnlyField()
    members = MemberSerializer(many=True, required=True)

    class Meta:
        model = Chat
        fields = ('type', 'channel', 'title', 'members')

    def validate_type(self, value):
        if value not in ChatTypes:
            raise serializers.ValidationError('invalid chat type')
        return value

    @transaction.atomic
    def create(self, validated_data):
        type = validated_data['type']
        chat = Chat(type=type)
        channel = Channel(app=app)
        while True:
            try:
                channel.channel = gen_channel_id()
                channel.save()
                break
            except IntegrityError:
                pass

        members = validated_data['members']
        for member in members:
            Member.objects.create(channel=channel, **member)
        channel.save()
        return channel
