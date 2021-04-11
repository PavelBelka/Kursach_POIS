import uuid

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Author(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)


class Genre(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class BookInstance(models.Model):
    id_security = models.UUIDField(default=uuid.uuid4)
    text = models.TextField()

    def __str__(self):
        return self.text


class Book(models.Model):
    title = models.CharField(max_length=256)
    authors = models.ManyToManyField(Author)
    isbn = models.CharField('ISBN', max_length=17)
    genre = models.ManyToManyField(Genre)
    id_inst = models.OneToOneField(BookInstance, on_delete=models.CASCADE, blank=True, null=True)

    BOOK_STATUS = (
        ('a', 'Available'),
        ('e', 'Expectation'),
        ('n_a', 'Not available')
    )

    status = models.CharField(max_length=3, choices=BOOK_STATUS, blank=True, default='n_a')

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    location = models.TextField(blank=True, null=True)
    phone = models.CharField(blank=True, null=True, max_length=12)
    date_joined = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)
    is_reader = models.BooleanField(default=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return self.user.username
