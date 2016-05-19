from .models import Chat, Member
from django.contrib import admin


class MemberInline(admin.TabularInline):
    model = Member
    can_delete = True
    verbose_name = 'member'


class ChatAdmin(admin.ModelAdmin):
    inlines = (MemberInline,)
    list_filter = ['type']
    search_fields = ['id', 'channel', 'title']
    list_display = ('id', 'type', 'channel', 'title', 'owner', 'created', 'updated')


admin.site.register(Chat, ChatAdmin)
