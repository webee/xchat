from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^t/$', views.test),
    url(r'^test/$', views.TestView.as_view()),
    url(r'^chats/(?P<chat_id>\d+).members$', views.MembersView.as_view(), name='members'),
    url(r'^chats/(?P<chat_id>\d+)/$', views.ChatView.as_view(), name='chat-detail'),
    url(r'^chats/$', views.CreateChatView.as_view(), name='create-chat'),
]
