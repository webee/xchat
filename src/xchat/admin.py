from .models import Room, Chat, Member, RoomChat
from django.contrib import admin


class RoomChatInline(admin.TabularInline):
    model = RoomChat
    extra = 1
    readonly_fields = ['id']


class RoomAdmin(admin.ModelAdmin):
    inlines = (RoomChatInline,)
    search_fields = ['id', 'title', 'tag']
    readonly_fields = ['id', 'created']
    list_display = ('id', 'title', 'tag', 'is_deleted', 'created')


class MemberInline(admin.TabularInline):
    model = Member
    extra = 1
    readonly_fields = ['id', 'joined', 'join_msg_id', 'cur_id', 'exit_msg_id']


class ChatAdmin(admin.ModelAdmin):
    inlines = (MemberInline,)
    list_filter = ['type', 'tag']
    search_fields = ['id', 'title', 'tag']
    readonly_fields = ['id', 'type', 'tag', 'msg_id', 'last_msg_ts', 'created', 'updated']
    list_display = ('id', 'type', 'title', 'tag', 'msg_id', 'last_msg_ts', 'is_deleted', 'updated', 'created')


admin.site.register(Room, RoomAdmin)
admin.site.register(Chat, ChatAdmin)
