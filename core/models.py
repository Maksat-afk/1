from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('volunteer', 'Волонтёр'),
        ('fund', 'Фонд'),
        ('sponsor', 'Спонсор'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Task(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)
    description = models.TextField()
    contacts = models.TextField(blank=True, null=True)
    expectations_sponsor = models.TextField(blank=True, null=True)
    expectations_volunteer = models.TextField(blank=True, null=True)
    volunteers_required = models.PositiveIntegerField(default=1)
    fund = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fund_tasks')
    volunteers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='accepted_tasks', blank=True)
    sponsors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='supported_tasks', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
    
class Review(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='written_reviews')
    target = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} → {self.target.username} ({self.rating})"

class Report(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_reports')
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reports')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
