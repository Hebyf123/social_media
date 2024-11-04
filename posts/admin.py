from django.contrib import admin
from .models import Hashtag, Post, Comment, PostReaction,CommentReaction

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user','title', 'created_at', 'text',)
    search_fields = ('user__email', 'text',)
    list_filter = ('created_at', 'user',)
    prepopulated_fields = {'text': ('hashtags',)} 
    
    def hashtags_list(self, obj):
        return ", ".join([hashtag.name for hashtag in obj.hashtags.all()])
    hashtags_list.short_description = 'Hashtags'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at', 'content')
    search_fields = ('post__text', 'user__email', 'content',)
    list_filter = ('created_at', 'post',)

@admin.register(PostReaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'reaction_type',)
    search_fields = ('user__email',)  
    list_filter = ('reaction_type',)



@admin.register(CommentReaction)
class CommentReaction(admin.ModelAdmin):
    list_display = ('user', 'reaction_type',)
    search_fields = ('user__email',)  
    list_filter = ('reaction_type',)

 