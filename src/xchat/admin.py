from .models import Chat, Member
from django.contrib import admin


class MemberInline(admin.TabularInline):
    model = Member
    extra = 1


class ChatAdmin(admin.ModelAdmin):
    inlines = (MemberInline,)
    list_filter = ['type', 'tag']
    search_fields = ['id', 'title']
    list_display = ('id', 'type', 'title', 'tag', 'created')


admin.site.register(Chat, ChatAdmin)
