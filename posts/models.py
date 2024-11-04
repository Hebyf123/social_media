from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.sessions.models import Session
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100,null =True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    viewed_ips = models.JSONField(default=list, blank=True,null=True)    
    text = models.TextField(verbose_name=_("Текст"), blank=True, null=True)
    audio = models.FileField(upload_to='post_audios/', blank=True, null=True, verbose_name=_("Аудио"))
    video = models.FileField(upload_to='post_videos/', blank=True, null=True, verbose_name=_("Видео"))
    image = models.ImageField(upload_to='post_images/', blank=True, null=True, verbose_name=_("Фото"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    hashtags = models.ManyToManyField(Hashtag, blank=True)
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество просмотров"))

    class Meta:
        verbose_name = _("Пост")
        verbose_name_plural = _("Посты")

    def __str__(self):
        return f'Post by {self.user.email} at {self.created_at}'

    def increment_views(self, ip_address=None, user=None, session_key=None):
        if user or ip_address or session_key:
            self.views_count += 1
            if ip_address and ip_address not in self.viewed_ips:
                self.viewed_ips.append(ip_address)
            self.save()


class Comment(models.Model):
    post = models.ForeignKey('Post', related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Comment by {self.user.name} on {self.post.title}'



class PostReaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user.username} reacted with {self.reaction_type} to post "{self.post.title}"'

class CommentReaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f'{self.user.username} reacted with {self.reaction_type} to comment "{self.comment.content}"'