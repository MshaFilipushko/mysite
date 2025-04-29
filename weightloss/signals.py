from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import F

from .models import Comment, RecipeComment, ForumPost, Post, Recipe, UserProfile, Notification


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """
    Отправляет уведомление автору поста при получении нового комментария
    """
    if created and instance.author != instance.post.author:
        # Уведомление автору поста о новом комментарии
        Notification.create_notification(
            recipient=instance.post.author,
            notification_type='comment',
            title='Новый комментарий к вашей статье',
            message=f'{instance.author.username} оставил(а) комментарий к вашей статье "{instance.post.title}"',
            sender=instance.author,
            content_object=instance,
            url=f"{instance.post.get_absolute_url()}#comment-{instance.id}"
        )
    
    # Если это ответ на комментарий, уведомляем автора родительского комментария
    if created and instance.parent and instance.author != instance.parent.author:
        Notification.create_notification(
            recipient=instance.parent.author,
            notification_type='reply',
            title='Новый ответ на ваш комментарий',
            message=f'{instance.author.username} ответил(а) на ваш комментарий к статье "{instance.post.title}"',
            sender=instance.author,
            content_object=instance,
            url=f"{instance.post.get_absolute_url()}#comment-{instance.id}"
        )


@receiver(post_save, sender=RecipeComment)
def create_recipe_comment_notification(sender, instance, created, **kwargs):
    """
    Отправляет уведомление автору рецепта при получении нового комментария
    """
    if created and instance.author != instance.recipe.author:
        # Уведомление автору рецепта о новом комментарии
        Notification.create_notification(
            recipient=instance.recipe.author,
            notification_type='comment',
            title='Новый комментарий к вашему рецепту',
            message=f'{instance.author.username} оставил(а) комментарий к вашему рецепту "{instance.recipe.title}"',
            sender=instance.author,
            content_object=instance,
            url=f"{instance.recipe.get_absolute_url()}#comment-{instance.id}"
        )
    
    # Если это ответ на комментарий, уведомляем автора родительского комментария
    if created and instance.parent and instance.author != instance.parent.author:
        Notification.create_notification(
            recipient=instance.parent.author,
            notification_type='reply',
            title='Новый ответ на ваш комментарий',
            message=f'{instance.author.username} ответил(а) на ваш комментарий к рецепту "{instance.recipe.title}"',
            sender=instance.author,
            content_object=instance,
            url=f"{instance.recipe.get_absolute_url()}#comment-{instance.id}"
        )


@receiver(post_save, sender=ForumPost)
def create_forum_post_notification(sender, instance, created, **kwargs):
    """
    Отправляет уведомление при получении нового ответа на форуме
    """
    if created and instance.parent and instance.author != instance.parent.author:
        # Уведомление автору родительского поста о новом ответе
        Notification.create_notification(
            recipient=instance.parent.author,
            notification_type='forum_reply',
            title='Новый ответ на ваше сообщение на форуме',
            message=f'{instance.author.username} ответил(а) на ваше сообщение в теме "{instance.topic.title}"',
            sender=instance.author,
            content_object=instance,
            url=f"{instance.get_absolute_url()}"
        )
    
    # Если это первый пост в теме, не нужно отправлять уведомление
    if created and not instance.parent:
        return
    
    # Если это новый пост в теме, уведомляем автора темы (если он не автор поста)
    if created and instance.author != instance.topic.author:
        Notification.create_notification(
            recipient=instance.topic.author,
            notification_type='forum_reply',
            title='Новое сообщение в вашей теме',
            message=f'{instance.author.username} оставил(а) сообщение в вашей теме "{instance.topic.title}"',
            sender=instance.author,
            content_object=instance,
            url=f"{instance.get_absolute_url()}"
        )


@receiver(post_save, sender=Post)
def create_post_status_notification(sender, instance, **kwargs):
    """
    Отправляет уведомление автору поста о изменении статуса публикации
    """
    try:
        # Проверяем, изменился ли статус поста
        if not hasattr(instance, '_previous_status'):
            return
        
        if instance._previous_status != instance.status:
            if instance.status == 'published':
                Notification.create_notification(
                    recipient=instance.author,
                    notification_type='status_update',
                    title='Ваша статья опубликована',
                    message=f'Ваша статья "{instance.title}" была проверена и опубликована',
                    url=instance.get_absolute_url()
                )
            elif instance.status == 'rejected':
                Notification.create_notification(
                    recipient=instance.author,
                    notification_type='status_update',
                    title='Статья не прошла модерацию',
                    message=f'Ваша статья "{instance.title}" не прошла модерацию',
                    url=reverse('user_posts')
                )
    except Exception:
        # Если произошла ошибка, просто пропускаем
        pass


@receiver(pre_save, sender=Post)
def store_previous_post_status(sender, instance, **kwargs):
    """
    Сохраняет предыдущий статус поста перед сохранением
    """
    try:
        prev_instance = Post.objects.get(pk=instance.pk)
        instance._previous_status = prev_instance.status
    except Post.DoesNotExist:
        instance._previous_status = None


@receiver(post_save, sender=Recipe)
def create_recipe_status_notification(sender, instance, **kwargs):
    """
    Отправляет уведомление автору рецепта о изменении статуса публикации
    """
    try:
        # Проверяем, изменился ли статус рецепта
        if not hasattr(instance, '_previous_status'):
            return
        
        if instance._previous_status != instance.status:
            if instance.status == 'published':
                Notification.create_notification(
                    recipient=instance.author,
                    notification_type='status_update',
                    title='Ваш рецепт опубликован',
                    message=f'Ваш рецепт "{instance.title}" был проверен и опубликован',
                    url=instance.get_absolute_url()
                )
            elif instance.status == 'rejected':
                Notification.create_notification(
                    recipient=instance.author,
                    notification_type='status_update',
                    title='Рецепт не прошел модерацию',
                    message=f'Ваш рецепт "{instance.title}" не прошел модерацию. Причина: {instance.rejection_reason or "Не указана"}',
                    url=reverse('user_recipes')
                )
    except Exception:
        # Если произошла ошибка, просто пропускаем
        pass


@receiver(pre_save, sender=Recipe)
def store_previous_recipe_status(sender, instance, **kwargs):
    """
    Сохраняет предыдущий статус рецепта перед сохранением
    """
    try:
        prev_instance = Recipe.objects.get(pk=instance.pk)
        instance._previous_status = prev_instance.status
    except Recipe.DoesNotExist:
        instance._previous_status = None


@receiver(post_save, sender=UserProfile)
def check_weight_goal_achievement(sender, instance, **kwargs):
    """
    Проверяет достижение целевого веса и отправляет уведомление
    """
    if instance.current_weight and instance.goal_weight:
        # Для случая снижения веса
        if instance.starting_weight > instance.goal_weight and instance.current_weight <= instance.goal_weight:
            Notification.create_notification(
                recipient=instance.user,
                notification_type='weight_goal',
                title='Поздравляем! 🎉',
                message=f'Вы достигли своей цели по весу! Ваш текущий вес {instance.current_weight} кг достиг или стал меньше целевого {instance.goal_weight} кг.',
                url=reverse('profile')
            )
        # Для случая набора веса
        elif instance.starting_weight < instance.goal_weight and instance.current_weight >= instance.goal_weight:
            Notification.create_notification(
                recipient=instance.user,
                notification_type='weight_goal',
                title='Поздравляем! 🎉',
                message=f'Вы достигли своей цели по весу! Ваш текущий вес {instance.current_weight} кг достиг или стал больше целевого {instance.goal_weight} кг.',
                url=reverse('profile')
            ) 