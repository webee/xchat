from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^t/$', views.test),
    url(r'^db/$', views.db),
    url(r'^test/$', views.TestView.as_view()),
    url(r'^chats/(?P<chat_id>\S+).members$', views.MembersView.as_view(), name='members'),
    url(r'^chats/(?P<chat_id>\S+)/$', views.ChatView.as_view(), name='chat-detail'),
    url(r'^chats/$', views.CreateChatView.as_view(), name='create-chat'),
    url(r'^user/chats/$', views.UserChatsView.as_view(), name='user-chats'),
    url(r'^rooms/(?P<room_id>\d+)/chats/$', views.RoomChatsView.as_view(), name='room-chats'),
]
