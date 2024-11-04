from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, URLValidator
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer

from .models import CustomUser, Friendship, Follower, Hashtag, Message, Chat, BugReport, Feedback, Notification
from posts.serializers import PostSerializer

class BugReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugReport
        fields = ['id', 'user', 'title', 'description', 'created_at', 'status']



class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'message', 'created_at']



class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ('id', 'name')
        ref_name = 'UsersHashtagSerializer'
class UserCreateSerializer(serializers.ModelSerializer):
    hashtags = serializers.PrimaryKeyRelatedField(many=True, queryset=Hashtag.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'password', 'name', 'surname',
            'photo', 'telegram_id', 'address', 'city', 'country', 'phone', 'hashtags'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'validators': [EmailValidator(message="Некорректный email.")]}
        }

    def create(self, validated_data):
        hashtags_data = validated_data.pop('hashtags', [])
        user = CustomUser.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        if hashtags_data:
            user.hashtags.set(hashtags_data)
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'hashtags']



class UserSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'username', 'name', 'surname',
            'photo', 'telegram_id', 'address', 'city', 'country', 'phone', 'hashtags'
        )


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'image', 'video', 'audio', 'is_edited', 'is_deleted', 'timestamp', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            validated_data['sender'] = request.user
        return super().create(validated_data)


class ChatSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'users', 'created_at', 'is_group', 'messages']


class UnfriendSerializer(serializers.Serializer):
    friend_id = serializers.IntegerField()

    def validate_friend_id(self, value):
        return validate_integer_field(value, "friend_id")

class UnfollowSerializer(serializers.Serializer):
    follower_id = serializers.IntegerField()


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    sender = UserSerializer(read_only=True, allow_null=True)
    post = PostSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'message', 'notification_type', 'post',
            'sender', 'created_at', 'is_read'
        ]



class FriendshipSerializer(serializers.ModelSerializer):
    friend_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=True)
    friend = serializers.StringRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, required=False)  # Сделаем поле user необязательным

    class Meta:
        model = Friendship
        fields = ['id', 'user','friend', 'friend_id', 'is_accepted', 'created_at']

class FollowerSerializer(serializers.ModelSerializer):
    follower = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Follower
        fields = ['id', 'user', 'follower', 'created_at']

class FollowBackSerializer(serializers.Serializer):
    follower_id = serializers.IntegerField()

