from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet,CommentReactionViewSet,CommentViewSet, PostReactionViewSet, HashtagViewSet
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi
router = DefaultRouter()


router.register(r'posts', PostViewSet)
router.register(r'posts/(?P<post_pk>[^/.]+)/comments', CommentViewSet, basename='post-comments')


router.register(r'post-reactions', PostReactionViewSet, basename='post-reactions')
router.register(r'comment-reactions', CommentReactionViewSet, basename='comment-reactions')


router.register(r'hashtags', HashtagViewSet)

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
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
