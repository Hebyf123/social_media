from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification, Friendship, Follower
from posts.models import PostReaction, CommentReaction, Post

@receiver(post_save, sender=PostReaction)
def send_post_reaction_notification(sender, instance, created, **kwargs):
    if created:
        reaction_type = 'like' if instance.reaction_type == 'like' else 'dislike'
        

        post = instance.post
        
        if post:
            Notification.objects.create(
                user=post.user,  
                sender=instance.user,  
                message=f'{instance.user.username} {reaction_type}d your post: "{post.title}".',
                notification_type=reaction_type,
                post=post
            )

@receiver(post_save, sender=CommentReaction)
def send_comment_reaction_notification(sender, instance, created, **kwargs):
    if created:
        reaction_type = 'like' if instance.reaction_type == 'like' else 'dislike'
        

        comment = instance.comment
        
        if comment:
            Notification.objects.create(
                user=comment.user,  
                sender=instance.user, 
                message=f'{instance.user.username} {reaction_type}d your comment: "{comment.content}".',
                notification_type=reaction_type, 
            )

@receiver(post_save, sender=Post)
def send_new_post_notification(sender, instance, created, **kwargs):
    if created:
        followers = instance.user.followers.all()  
        for follower in followers:
            Notification.objects.create(
                user=follower.follower,  
                sender=instance.user, 
                message=f'{instance.user.name} has posted a new update.',
                notification_type='new_post',
                post=instance  
            )

@receiver(post_save, sender=Friendship)
def send_friend_request_notification(sender, instance, created, **kwargs):
    if created and not instance.is_accepted:  
        Notification.objects.create(
            user=instance.friend,  
            sender=instance.user,  
            message=f'{instance.user.name} sent you a friend request.',
            notification_type='friend_request'
        )

@receiver(post_save, sender=Follower)
def send_follow_notification(sender, instance, created, **kwargs):
    if created: 
        Notification.objects.create(
            user=instance.user,  
            sender=instance.follower,  
            message=f'{instance.follower.name} started following you.',
            notification_type='follow'
        )
