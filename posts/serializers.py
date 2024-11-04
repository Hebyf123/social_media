from rest_framework import serializers
from .models import Post, Comment, Hashtag
from .models import PostReaction, CommentReaction
class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['id', 'name']
        ref_name = 'PostsHashtagSerializer'



class PostReactionSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    class Meta:
        model = PostReaction
        fields = ['id', 'post', 'reaction_type','like_count', 'dislike_count']
    def get_like_count(self, obj):
        return PostReaction.objects.filter(post=obj.post, reaction_type='like').count()

    def get_dislike_count(self, obj):
        return PostReaction.objects.filter(post=obj.post, reaction_type='dislike').count()

class CommentReactionSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    class Meta:
        model = CommentReaction
        fields = ['id', 'comment', 'reaction_type','like_count', 'dislike_count']
    def get_like_count(self, obj):
        return CommentReaction.objects.filter(comment=obj.comment, reaction_type='like').count()

    def get_dislike_count(self, obj):
        return CommentReaction.objects.filter(comment=obj.comment, reaction_type='dislike').count()
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    reactions = CommentReactionSerializer(many=True, read_only=True)  

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at', 'parent_comment', 'replies', 'reactions']  
        read_only_fields = ['user', 'created_at']

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data
class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)  
    reactions = PostReactionSerializer(many=True, read_only=True)  
    comments_count = serializers.SerializerMethodField()
    hashtags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'user', 'text', 'audio', 'video', 'image',
            'created_at', 'hashtags', 'views_count', 'comments_count',
            'comments', 'reactions'  
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        hashtags_data = validated_data.pop('hashtags', [])
        post = Post.objects.create(**validated_data)

        for hashtag_data in hashtags_data:
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_data['name'])
            post.hashtags.add(hashtag)

        return post


