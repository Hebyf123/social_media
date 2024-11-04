from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import CustomUser, Friendship, Hashtag, Follower, Chat, Message, BugReport, Feedback, Notification
from .serializers import (
    FriendshipSerializer, UnfriendSerializer, UserSerializer,
    UnfollowSerializer, CustomUserSerializer, HashtagSerializer,
    FollowerSerializer, NotificationSerializer, FollowBackSerializer,
    ChatSerializer, MessageSerializer, BugReportSerializer, FeedbackSerializer
)

from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

User = get_user_model()

class BugReportViewSet(viewsets.ModelViewSet):
    queryset = BugReport.objects.all()
    serializer_class = BugReportSerializer
    permission_classes = [permissions.IsAuthenticated]

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

class FullUserListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['id']
    search_fields = ['name']

class UserListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['hashtags']
    search_fields = ['name']

class ChatHistoryView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        return Message.objects.filter(chat_id=chat_id).order_by('-timestamp')

class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        name_query = self.request.query_params.get('name', None)
        hashtag_query = self.request.query_params.get('hashtag', None)
        queryset = CustomUser.objects.all()

        if name_query:
            queryset = queryset.filter(name__icontains=name_query)

        if hashtag_query:
            queryset = queryset.filter(hashtags__name__icontains=hashtag_query)

        return queryset.distinct()

class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Friendship.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='add-friend/(?P<friend_id>[^/.]+)')
    def add_friend(self, request, friend_id=None):
        friend = get_object_or_404(CustomUser, id=friend_id)

        if request.user.id == friend.id:
            return Response({'message': 'You cannot add yourself as a friend'}, status=status.HTTP_400_BAD_REQUEST)

        friendship, created = Friendship.objects.get_or_create(user=request.user, friend=friend)

        if created:
            return Response({'message': f'You are now friends with {friend.email}'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'You are already friends with this user'}, status=status.HTTP_409_CONFLICT)

    @action(detail=False, methods=['get'], url_path='friends-of/(?P<user_id>[^/.]+)')
    def get_friends_of_user(self, request, user_id=None):
        user = get_object_or_404(CustomUser, pk=user_id)
        friends = Friendship.objects.filter(user=user, is_accepted=True)
        serializer = self.get_serializer(friends, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='unfriend')
    def unfriend(self, request):
        serializer = UnfriendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        friend_id = serializer.validated_data['friend_id']
        friend = get_object_or_404(CustomUser, id=friend_id)

        friendship = Friendship.objects.filter(user=request.user, friend=friend)
        if friendship.exists():
            friendship.delete()
            return Response({'message': f'You are no longer friends with {friend.name}'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Friendship does not exist'}, status=status.HTTP_404_NOT_FOUND)

class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Follower.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='followers-of/(?P<user_id>[^/.]+)')
    def get_followers_of_user(self, request, user_id=None):
        user = get_object_or_404(CustomUser, pk=user_id)
        followers = Follower.objects.filter(user=user)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='follow-back')
    def follow_back(self, request):
        serializer = FollowBackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        follower_id = serializer.validated_data['follower_id']
        follower = get_object_or_404(CustomUser, id=follower_id)

        if request.user.id == follower.id:
            return Response({'message': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        Follower.objects.get_or_create(user=request.user, follower=follower)
        return Response({'message': f'You are now following back {follower.name}'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='unfollow')
    def unfollow(self, request):
        serializer = UnfollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        follower_id = serializer.validated_data['follower_id']
        follower = get_object_or_404(CustomUser, id=follower_id)
        following = Follower.objects.filter(user=request.user, follower=follower)
        if following.exists():
            following.delete()
            return Response({'message': f'You are no longer following {follower.name}'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'You are not following this user'}, status=status.HTTP_404_NOT_FOUND)

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    @action(detail=True, methods=['post'], url_path='join/(?P<invite_link>[^/.]+)')
    def join_group_chat(self, request, *args, **kwargs):
        chat_id = self.kwargs.get('pk')
        invite_link = kwargs.get('invite_link')

        chat = get_object_or_404(Chat, id=chat_id, is_group=True)

        if chat.invite_link != invite_link:
            return Response({"detail": "Invalid invite link."}, status=status.HTTP_400_BAD_REQUEST)

        chat.users.add(request.user)
        chat.save()
        return Response({"chat_id": chat.id}, status=status.HTTP_200_OK)

    def create_group_chat(self, request, *args, **kwargs):
        user_ids = request.data.get('user_ids', [])
        users = CustomUser.objects.filter(id__in=user_ids)

        if len(users) != len(user_ids):
            return Response({"detail": "One or more users not found."}, status=status.HTTP_400_BAD_REQUEST)

        users = list(users) + [request.user]

        with transaction.atomic():
            chat = Chat.objects.create(is_group=True)
            chat.users.add(*users)

        return Response({"chat_id": chat.id}, status=status.HTTP_201_CREATED)

class NotificationViewSet(viewsets.ModelViewSet): 
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_destroy(self, instance):
        instance.delete()

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        chat_id = request.data.get('chat_id')
        content = request.data.get('content')
        message = Message.objects.create(chat_id=chat_id, sender=request.user, content=content)
        return Response({"message_id": message.id}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        message.content = request.data.get('content')
        message.is_edited = True
        message.save()
        return Response({"message_id": message.id}, status=status.HTTP_200_OK)
    @action(detail=False, methods=['post'], url_path='upload', permission_classes=[IsAuthenticated])
    def upload_media(self, request, *args, **kwargs):
        chat_id = request.data.get('chat_id')
        chat = Chat.objects.get(id=chat_id)

        if not chat.users.filter(id=request.user.id).exists():
            return Response({"detail": "Вы не являетесь участником этого чата."}, status=status.HTTP_403_FORBIDDEN)


        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=request.data.get('content')
        )


        if 'audio' in request.FILES:
            message.audio = request.FILES['audio']
        if 'files' in request.FILES:
            for file in request.FILES.getlist('files'):
               
                if file.content_type.startswith('image/'):
                    message.image = file  
                elif file.content_type.startswith('video/'):
                    message.video = file  
                elif file.content_type.startswith('audio/'):
                    message.audio = file  

        message.save()  

        return Response({"message_id": message.id}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class HashtagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer