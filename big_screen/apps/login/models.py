from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
