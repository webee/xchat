from .models import Chat, Member, DeviceInfo
from django.contrib import admin


class MemberInline(admin.TabularInline):
    model = Member
    extra = 1


class ChatAdmin(admin.ModelAdmin):
    inlines = (MemberInline,)
    list_filter = ['type', 'tag']
    search_fields = ['id', 'title']
    list_display = ('id', 'type', 'title', 'tag', 'created')


class DeviceInfoAdmin(admin.ModelAdmin):
    list_filter = ['user', 'dev']
    search_fields = ['user', 'dev', 'dev_id']
    list_display = ('user', 'dev', 'dev_id')


admin.site.register(Chat, ChatAdmin)
admin.site.register(DeviceInfo, DeviceInfoAdmin)
