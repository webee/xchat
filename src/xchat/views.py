from django.db import transaction
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.http.response import JsonResponse
import xim_client
import time
from .models import Chat, ChatType, User
from .serializers import ChatSerializer, MembersSerializer, MemberSerializer


def test(request):
    return JsonResponse({'ok': True, 't': time.time()})


class TestView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        return Response({'ok': True, 't': time.time()})


class UserChatsView(APIView):
    permission_classes = (IsAdminUser,)

    def get_user(self, user):
        try:
            return User.objects.get(user=user)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        user = request.data.get("user")
        user = self.get_user(user)
        t = request.data.get("type")
        tag = request.data.get("tag")
        q = user.chats
        if t is not None:
            q = q.filter(type=t)
        if tag is not None:
            q = q.filter(tag=tag)
        chats = q.all()
        return Response([{"id": chat.id, "type": chat.type, "title": chat.title, "tag": chat.tag} for chat in chats])


class CreateChatView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            try:
                chat = serializer.save()
                return Response({"id": chat.id}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatView(APIView):
    """
    get, search chats.
    """
    def get_queryset(self, chat_id):
        return Chat.objects.filter(id=chat_id, is_deleted=False)

    def get_chat(self, chat_id):
        try:
            return self.get_queryset(chat_id).get()
        except Chat.DoesNotExist:
            raise Http404

    def get(self, request, chat_id, format=None):
        chat = self.get_chat(chat_id)
        serializer = ChatSerializer(chat, context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, chat_id):
        client = xim_client.get_client()
        chat = self.get_chat(chat_id)
        if client.close_channel(chat.channel):
            _ = self.get_queryset(chat_id).update(is_deleted=True)
            return Response({'ok': True})
        return Response({'ok': False})


class MembersView(APIView):
    """
    get, add, remove chat members.
    """
    def get_chat(self, chat_id):
        try:
            return Chat.objects.get(id=chat_id, is_deleted=False)
        except Chat.DoesNotExist:
            raise Http404

    def get(self, request, chat_id, format=None):
        chat = self.get_chat(chat_id)
        serializer = MemberSerializer(chat.member_set.all(), many=True)
        return Response(serializer.data)

    def post(self, request, chat_id, format=None):
        chat = self.get_chat(chat_id)
        if chat.type in [ChatType.SELF, ChatType.USER]:
            return Response({'ok': False}, status=status.HTTP_403_FORBIDDEN)
        serializer = MembersSerializer(data=request.data)
        if serializer.is_valid():
            ret = serializer.save(chat=chat)
            if ret:
                return Response({
                    'ok': True
                }, status=status.HTTP_201_CREATED)
            return Response({
                'ok': False
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, chat_id, format=None):
        chat = self.get_chat(chat_id)
        if chat.type in [ChatType.SELF, ChatType.USER]:
            return Response({'ok': False}, status=status.HTTP_403_FORBIDDEN)

        serializer = MembersSerializer(data=request.data)
        if serializer.is_valid():
            users = serializer.validated_data['users']
            client = xim_client.get_client()
            if client.remove_channel_subscribers(chat.channel, users):
                if client.remove_channel_publishers(chat.channel, users):
                    deleted, _ = chat.member_set.filter(user__user__in=users).delete()
                    if deleted > 0:
                        chat.save()
                    return Response({
                        'ok': True,
                        'deleted': deleted
                    }, status=status.HTTP_200_OK)
            return Response({
                'ok': False,
                'deleted': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
