from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Staff-only user. There is no public registration in the MVP."""

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.get_username()
