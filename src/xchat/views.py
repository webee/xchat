from django.db import transaction
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import Chat, ChatType, Member, Room
from .serializers import ChatSerializer, MembersSerializer, MemberSerializer, MessagesSerializer
from pytoolbox.jwt import encode_ns_user
from .serializers import set_update_chat, update_chat_members


class UserChatsView(APIView):
    def get(self, request):
        user = request.query_params.get("user")
        t = request.query_params.get("type")
        tag = request.query_params.get("tag")
        members = Member.objects.select_related().filter(user=user)
        if t:
            members = members.filter(chat__type=t)
        if tag:
            members = members.filter(chat__tag=tag)
        return Response([{"id": m.chat.chat_id, "type": m.chat.type, "title": m.chat.title, "tag": m.chat.tag, 'msg_id': m.chat.msg_id, 'ext': m.chat.ext} for m in members])


class CreateChatView(APIView):
    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            try:
                chat = serializer.save(ns=request.user.ns)
                return Response({"id": chat.chat_id}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatView(APIView):
    """
    get, search chats.
    """
    def get_queryset(self, chat_id):
        chat_id = int(chat_id.split('.', 1)[1])
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

    def post(self, request, chat_id):
        chat = self.get_chat(chat_id)
        data = dict(request.data)
        data.update(dict(type=chat.type, biz_id=chat.biz_id))
        serializer = ChatSerializer(data=data)
        if serializer.is_valid():
            app_id = serializer.validated_data.get('app_id')
            title = serializer.validated_data.get('title')
            tag = serializer.validated_data.get('tag')
            ext = serializer.validated_data.get('ext')

            set_update_chat(chat, app_id, title, tag, ext)
            chat.save()

            return Response({'ok': True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, chat_id):
        _ = self.get_queryset(chat_id).update(is_deleted=True)
        return Response({'ok': True})


class RoomChatsView(APIView):
    """
    get, search rooms.
    """
    def get_room(self, room_id):
        try:
            return Room.objects.get(pk=room_id)
        except Room.DoesNotExist:
            raise Http404

    def get(self, request, room_id):
        room = self.get_room(room_id)
        chats = [chat.chat.chat_id for chat in room.chats.select_related().order_by('area').all()]
        return Response(chats)


class MembersView(APIView):
    """
    get, add, remove chat members.
    """
    def get_chat(self, chat_id):
        chat_id = int(chat_id.split('.', 1)[1])
        try:
            return Chat.objects.get(id=chat_id, is_deleted=False)
        except Chat.DoesNotExist:
            raise Http404

    def get(self, request, chat_id, format=None):
        """获取会话成员"""
        chat = self.get_chat(chat_id)
        serializer = MemberSerializer(chat.members.all(), many=True)
        return Response(serializer.data)

    def post(self, request, chat_id, format=None):
        """添加会话成员"""
        chat = self.get_chat(chat_id)
        # 只能给群组会话增加成员
        if chat.type not in [ChatType.GROUP]:
            return Response({'ok': False}, status=status.HTTP_403_FORBIDDEN)
        serializer = MembersSerializer(data=request.data)
        if serializer.is_valid():
            _ = serializer.save(ns=request.user.ns, chat=chat)
            return Response({
                'ok': True
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, chat_id, format=None):
        """删除会话成员"""
        chat = self.get_chat(chat_id)
        # 只能从群组会话删除成员
        if chat.type not in [ChatType.GROUP]:
            return Response({'ok': False}, status=status.HTTP_403_FORBIDDEN)

        serializer = MembersSerializer(data=request.data)
        if serializer.is_valid():
            ns = request.user.ns
            users = serializer.validated_data['users']
            users = [encode_ns_user(ns, user) for user in users]
            # TODO: 标记is_exited.
            deleted, _ = chat.members.filter(user__in=users).delete()
            if deleted > 0:
                # update
                chat.update_members_updated()
            return Response({
                'ok': True
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, chat_id, format=None):
        """替换会话成员"""
        chat = self.get_chat(chat_id)
        # 只能从群组会话删除成员
        if chat.type not in [ChatType.GROUP]:
            return Response({'ok': False}, status=status.HTTP_403_FORBIDDEN)

        serializer = MembersSerializer(data=request.data)
        if serializer.is_valid():
            ns = request.user.ns
            users = serializer.validated_data['users']
            users = [encode_ns_user(ns, user) for user in users]

            update_chat_members(chat, users)
            return Response({
                'ok': True
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatMessagesView(APIView):
    """
    insert chat messages.
    """
    def get_chat(self, chat_id):
        chat_id = int(chat_id.split('.', 1)[1])
        try:
            return Chat.objects.get(id=chat_id, is_deleted=False)
        except Chat.DoesNotExist:
            raise Http404

    def post(self, request, chat_id):
        """向前插入消息"""
        data = request.data
        chat = self.get_chat(chat_id)
        if chat.start_msg_id <= 0:
            return Response({'ok': False})

        serializer = MessagesSerializer(data=data)
        if serializer.is_valid():
            n = serializer.save(ns=request.user.ns, chat=chat)
            return Response({
                'ok': True, 'n': n
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
