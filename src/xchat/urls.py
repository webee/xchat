from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^t/', views.test),
    url(r'^test/$', views.TestView.as_view()),
]
