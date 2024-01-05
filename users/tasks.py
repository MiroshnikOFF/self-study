from django.core.mail import send_mail
from celery import shared_task

from config import settings


@shared_task
def send_verification_code(email: str, key: str) -> None:
    """ Отправляет код для верификации электронной почты на email пользователя """

    send_mail(
        subject='Подтверждение электронной почты',
        message=f'Код для подтверждения: {key}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )


@shared_task
def send_new_password(email: str, new_password: str) -> None:
    """ Отправляет новый пароль на email пользователя """

    send_mail(
        subject='Восстановление доступа',
        message=f'Ваш новый пароль: {new_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )
