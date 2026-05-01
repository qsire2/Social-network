from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='default.jpg')
    bio = models.TextField(max_length=500, blank=True)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)

    def __str__(self):
        return f"Профіль {self.user.username}"

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)

    def __str__(self):
        return f"Пост від {self.author.username} ({self.created_at.strftime('%d.%m %H:%M')})"
