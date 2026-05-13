from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from config.logger import logger

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """логируем вход пользователя в систему"""
    logger.info(f"пользователь {user.username} вошел в систему")
