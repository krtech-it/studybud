from django.contrib import admin
from .models import Room, Topic, Message, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
     list_display = ('email', 'username',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
     list_display = ('name', 'host', 'topic')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
     list_display = ('user', 'room', 'body')
     list_display_links = ('body',)

admin.site.register(Topic)
