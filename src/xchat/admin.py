from .models import App, Room, Chat, Member, RoomChat
from django.contrib import admin


class AppAdmin(admin.ModelAdmin):
    search_fields = ['app_id']
    readonly_fields = ['id', 'created', 'updated']
    list_display = ('id', 'app_id', 'created', 'updated')


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
    search_fields = ['id', 'biz_id', 'app_id', 'title', 'tag']
    list_display = ('id', 'type', 'key', 'biz_id', 'app_id', 'title', 'tag', 'start_msg_id', 'msg_id', 'last_msg_ts',
                    'is_deleted', 'updated', 'members_updated', 'created')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            readonly_fields = ['id', 'type', 'tag', 'owner', 'msg_id', 'last_msg_ts', 'created', 'updated',
                               'members_updated']
        else:
            readonly_fields = ['id', 'owner', 'msg_id', 'last_msg_ts', 'created', 'updated', 'members_updated']
        return readonly_fields


admin.site.register(App, AppAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Chat, ChatAdmin)
