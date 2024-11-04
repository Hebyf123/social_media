from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext as _
from posts.models import Post
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  
    name = models.CharField(max_length=80, verbose_name=_("Имя"), blank=True, null=True)
    surname = models.CharField(max_length=80, verbose_name=_("Фамилия"), blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True, verbose_name=_("Фото"))
    telegram_id = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Telegram ID"))
    country = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Страна"))
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Город"))
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Адрес"))
    phone = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Телефон"))
    friends_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество друзей"))
    followers_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество подписчиков"))
    last_online = models.DateTimeField(null=True, blank=True, verbose_name=_("Последний раз в сети"))
    status = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Статус"))
    hashtags = models.ManyToManyField(Hashtag, related_name='users', blank=True)

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        elif not self.email:
            self.email = self.username
        
        super().save(*args, **kwargs)



class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_post', 'New Post'),
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('friend_request', 'Friend Request'),
        ('follow', 'Follow'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='new_post')
    post = models.ForeignKey('posts.Post', null=True, blank=True, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE, related_name='sent_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'


class Friendship(models.Model):
    user = models.ForeignKey(CustomUser, related_name='friendships', on_delete=models.CASCADE)
    friend = models.ForeignKey(CustomUser, related_name='friends', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False, verbose_name=_("Принят"))

    def __str__(self):
        return f'{self.user.name} -> {self.friend.name}'


class Follower(models.Model):
    user = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.follower.name} подписан на {self.user.name}'


class Chat(models.Model):
    users = models.ManyToManyField(CustomUser, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)
    is_group = models.BooleanField(default=False)
    invite_link = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.invite_link:
            self.invite_link = str(uuid.uuid4())
        super().save(*args, **kwargs)


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)  
    media = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    video = models.FileField(upload_to='chat_videos/', blank=True, null=True)
    audio = models.FileField(upload_to='chat_audio/', blank=True, null=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:  
            self.is_edited = True
        super().save(*args, **kwargs)


class BugReport(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='open')  # open, resolved, etc.

    def __str__(self):
        return self.title


class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.user.username} at {self.created_at}'