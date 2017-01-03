from .models import Room, Chat, Member, RoomChat
from django.contrib import admin


class RoomChatInline(admin.TabularInline):
    model = RoomChat
    extra = 1
    readonly_fields = ['id']
    raw_id_fields = ['chat']


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
    list_display = ('id', 'type', 'title', 'tag', 'msg_id', 'last_msg_ts', 'is_deleted', 'updated', 'created')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            readonly_fields = ['id', 'type', 'tag', 'msg_id', 'last_msg_ts', 'created', 'updated']
        else:
            readonly_fields = ['id', 'msg_id', 'last_msg_ts', 'created', 'updated']
        return readonly_fields


admin.site.register(Room, RoomAdmin)
admin.site.register(Chat, ChatAdmin)
