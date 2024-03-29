from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    REVIEWER = 'REVIEWER'
    READER = 'READER'

    ROLE_CHOICES = (
        (REVIEWER, 'Rédacteur'),
        (READER, 'Lecteur'),
    )

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, verbose_name='Rôle')
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followed_by',
        verbose_name='followers'
    )
