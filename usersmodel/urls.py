from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FriendshipViewSet, FollowerViewSet,UserListViewSet,FullUserListViewSet, HashtagViewSet,UserSearchView, ChatViewSet,NotificationViewSet, MessageViewSet,ChatHistoryView,BugReportViewSet,FeedbackViewSet
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi
router = DefaultRouter()

router.register(r'friendships', FriendshipViewSet, basename='friendship')
router.register(r'followers', FollowerViewSet, basename='follower')
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'bug-reports', BugReportViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'allusers', UserListViewSet, basename='user')
router.register(r'Notification',NotificationViewSet)
router.register(r'hashtags', HashtagViewSet, basename='hashtag')
router.register(r'usersinfo', FullUserListViewSet, basename='users')


schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API для работы с продуктами, категориями, вариантами и отзывами.",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=False,  
    permission_classes=(permissions.IsAdminUser,),
)
urlpatterns = [
    path('users/search/', UserSearchView.as_view(), name='user-search'),
    path('api/chat/<int:chat_id>/history/', ChatHistoryView.as_view(), name='chat-history'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', include(router.urls)),   

]

