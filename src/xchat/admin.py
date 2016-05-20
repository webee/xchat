from .models import Chat, Member, User
from django.contrib import admin


class UserAdmin(admin.ModelAdmin):
    search_fields = ['id', 'user']
    list_display = ('id', 'user')


class MemberInline(admin.TabularInline):
    model = Member
    extra = 1


class ChatAdmin(admin.ModelAdmin):
    inlines = (MemberInline,)
    list_filter = ['type', 'tag']
    search_fields = ['id', 'channel', 'title']
    list_display = ('id', 'type', 'channel', 'title', 'owner', 'tag', 'created', 'updated')


admin.site.register(User, UserAdmin)
admin.site.register(Chat, ChatAdmin)
