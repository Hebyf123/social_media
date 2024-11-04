from django.db.models import Q, Count, OuterRef, Subquery
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post, Comment, Hashtag, PostReaction, CommentReaction
from .serializers import CommentSerializer, PostSerializer, HashtagSerializer, PostReactionSerializer, CommentReactionSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if 'post_pk' in self.kwargs:
            return Comment.objects.filter(post=self.kwargs['post_pk']).order_by('-created_at')
        return Comment.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, post=self.get_post())

    def get_post(self):
        from posts.models import Post  
        return Post.objects.get(pk=self.kwargs['post_pk'])

    @action(detail=False, methods=['get'], url_path='all-comments')
    def list_all_comments(self, request):
        all_comments = Comment.objects.all().order_by('-created_at')
        serializer = self.get_serializer(all_comments, many=True)
        return Response(serializer.data)


class PostReactionViewSet(viewsets.ModelViewSet):
    queryset = PostReaction.objects.all()
    serializer_class = PostReactionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.order_by('post')


class CommentReactionViewSet(viewsets.ModelViewSet):
    queryset = CommentReaction.objects.all()
    serializer_class = CommentReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('comment')  


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
   
    def get_queryset(self):
        queryset = super().get_queryset()  
    
        user_id = self.request.query_params.get('user')
        hashtag_param = self.request.query_params.get('hashtags')  
        title_query = self.request.query_params.get('title')
        sort_by = self.request.query_params.get('sortBy', 'views')
        likes_count = self.request.query_params.get('likes_count')
        dislikes_count = self.request.query_params.get('dislikes_count')
        
        if user_id:
            queryset = queryset.filter(user__id=user_id)
    
        if hashtag_param:
            hashtags = hashtag_param.split(',')  
            queryset = queryset.filter(Q(hashtags__id__in=hashtags)).distinct()  
    
        if title_query:
            queryset = queryset.filter(title__icontains=title_query)
    
    
        if sort_by == 'views':
            queryset = queryset.order_by('-views_count')  
        elif sort_by == 'likes':
            queryset = queryset.annotate(like_count=Count('reactions', filter=Q(reactions__reaction_type='like'))).order_by('-like_count') 
        elif sort_by == 'dislikes':
            queryset = queryset.annotate(dislike_count=Count('reactions', filter=Q(reactions__reaction_type='dislike'))).order_by('-dislike_count')  
        return queryset  
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        ip_address = get_client_ip(request)
        viewed_ips_set = {ip for post in queryset for ip in post.viewed_ips}
        posts_to_update = []
    
        for post in queryset:
            if ip_address and ip_address not in viewed_ips_set:
                post.increment_views(ip_address=ip_address)
                posts_to_update.append(post)
    
        if posts_to_update:
            with transaction.atomic():
                for post in posts_to_update:
                    post.save()  
    
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
    
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()
    
        session_key = request.session.session_key
        if not session_key:
            request.session.create() 
            session_key = request.session.session_key
        
        ip_address = get_client_ip(request)
       
        if request.user.is_authenticated:
            post.increment_views(user=request.user)
        elif session_key:
            post.increment_views(session_key=session_key)
        elif ip_address:
            post.increment_views(ip_address=ip_address)
    
        serializer = self.get_serializer(post)
        return Response(serializer.data)


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]