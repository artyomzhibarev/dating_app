from app.models import User, Match
from django.core.mail import send_mail


def send_email_to_user(data: dict):
    for item in data.values():
        send_mail(
            subject='From dating app',
            message=f"Вы понравились {item[0]}",
            recipient_list=[item[1]],
            from_email='dating@app.com',
            fail_silently=False,
        )


def check_match_between_users(user_id: int, user_2_id: int):
    """
    Checks the match between users and sends the user's email
    :param user_2_id:
    :param user_id:
    :return:
    """
    if Match.objects.filter(
            from_user_id=user_id,
            liked_user_id=user_2_id).exists():
        return User.objects.get(pk=user_id).email
