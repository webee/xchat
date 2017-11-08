from django.conf.urls import url

from . import views, test_views
from . import stat_views

urlpatterns = [
    # test views
    url(r'^t/$', test_views.test),
    url(r'^db/$', test_views.db),
    url(r'^test/$', test_views.TestView.as_view()),

    # xchat views
    url(r'^chats/(?P<chat_id>\w*\.\d+).members$', views.MembersView.as_view(), name='members'),
    url(r'^chats/(?P<chat_id>\w*\.\d+)/$', views.ChatView.as_view(), name='chat-detail'),
    url(r'^chats/$', views.CreateChatView.as_view(), name='create-chat'),
    url(r'^user/chats/$', views.UserChatsView.as_view(), name='user-chats'),
    url(r'^rooms/(?P<room_id>\d+)/chats/$', views.RoomChatsView.as_view(), name='room-chats'),

    url(r'^chats/(?P<chat_id>\w*\.\d+)/msgs/$', views.ChatMessagesView.as_view(), name='messages'),

    # stats
    url(r'^stat/chat/user/msgs/$', stat_views.StatChatUserMsgsView.as_view(), name='stat-chat-user-msgs'),
]
