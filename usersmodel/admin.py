from django.contrib import admin
from .models import CustomUser, Hashtag, Notification, Friendship, Follower, Chat, Message

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'name', 'surname', 'friends_count', 'followers_count', 'last_online', 'is_staff')
    search_fields = ('email', 'name', 'surname')
    list_filter = ('is_staff', 'is_active', 'last_online')
    ordering = ('email',)

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message',)
    ordering = ('-created_at',)

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('user__email', 'friend__email')
    ordering = ('-created_at',)

@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('user', 'follower', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'follower__email')
    ordering = ('-created_at',)

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_group', 'created_at')
    list_filter = ('is_group', 'created_at')
    ordering = ('-created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'timestamp', 'is_edited', 'is_deleted')
    list_filter = ('is_edited', 'is_deleted', 'timestamp')
    search_fields = ('content', 'sender__email')
    ordering = ('-timestamp',)
