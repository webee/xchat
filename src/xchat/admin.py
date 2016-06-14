from .models import Room, Chat, Member
from django.contrib import admin


class ChatInline(admin.TabularInline):
    model = Chat
    extra = 1


class RoomAdmin(admin.ModelAdmin):
    inlines = (ChatInline,)
    search_fields = ['id', 'title', 'tag']
    list_display = ('id', 'title', 'tag', 'is_deleted', 'created')


class MemberInline(admin.TabularInline):
    model = Member
    extra = 1


class ChatAdmin(admin.ModelAdmin):
    inlines = (MemberInline,)
    list_filter = ['type', 'tag']
    search_fields = ['id', 'title', 'tag']
    list_display = ('id', 'type', 'title', 'tag', 'room', 'is_deleted', 'updated', 'created')


admin.site.register(Room, RoomAdmin)
admin.site.register(Chat, ChatAdmin)
