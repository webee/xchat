from django.db import transaction, models
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.http.response import JsonResponse
import time
from .models import Chat, ChatType, Member
from .serializers import ChatSerializer, MembersSerializer, MemberSerializer


def test(request):
    return JsonResponse({'ok': True, 't': time.time()})


class TestView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        return Response({'ok': True, 't': time.time()})


class UserChatsView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        user = request.query_params.get("user")
        t = request.query_params.get("type")
        tag = request.query_params.get("tag")
        members = Member.objects.select_related().filter(user=user)
        if t:
            members = members.filter(chat__type=t)
        if tag:
            members = members.filter(chat__tag=tag)
        return Response([{"id": m.chat.id, "type": m.chat.type, "title": m.chat.title, "tag": m.chat.tag, 'msg_id': m.chat.msg_id} for m in members])


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

    def get(self, request, chat_id):
        chat = self.get_chat(chat_id)
        serializer = ChatSerializer(chat, context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, chat_id):
        _ = self.get_queryset(chat_id).update(is_deleted=True)
        return Response({'ok': True})


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
        serializer = MemberSerializer(chat.members.all(), many=True)
        return Response(serializer.data)

    def post(self, request, chat_id, format=None):
        chat = self.get_chat(chat_id)
        if chat.type in [ChatType.SELF, ChatType.USER]:
            return Response({'ok': False}, status=status.HTTP_403_FORBIDDEN)
        serializer = MembersSerializer(data=request.data)
        if serializer.is_valid():
            _ = serializer.save(chat=chat)
            return Response({
                'ok': True
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, chat_id, format=None):
        chat = self.get_chat(chat_id)
        if chat.type in [ChatType.SELF, ChatType.USER]:
            return Response({'ok': False}, status=status.HTTP_403_FORBIDDEN)

        serializer = MembersSerializer(data=request.data)
        if serializer.is_valid():
            users = serializer.validated_data['users']
            deleted, _ = chat.members.filter(user__in=users).delete()
            if deleted > 0:
                # update
                chat.save()
            return Response({
                'ok': True
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
