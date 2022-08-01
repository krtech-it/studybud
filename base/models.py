from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True, verbose_name='имя')
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, verbose_name='обо мне')

    avatar = models.ImageField(null=True, default='avatar.svg', verbose_name='аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []



class Topic(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='автор')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, verbose_name="тема")
    name = models.CharField(max_length=200, verbose_name="название")
    description = models.TextField(null=True, blank=True, verbose_name='описание')
    participants = models.ManyToManyField(User, related_name='participants', blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room =  models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментариии'

    def __str__(self):
        return self.body[:50]
