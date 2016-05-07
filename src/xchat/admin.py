from .models import Chat, Member
from django.contrib import admin


class MemberInline(admin.TabularInline):
    model = Member
    can_delete = True
    verbose_name = 'member'


class ChatAdmin(admin.ModelAdmin):
    inlines = (MemberInline,)
    list_filter = ['type']
    search_fields = ['channel', 'title']
    list_display = ('type', 'channel', 'title', 'created')


admin.site.register(Chat, ChatAdmin)
