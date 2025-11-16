from django.db import models
from django.contrib.auth.models import User


class SocialToken(models.Model):
    PROVIDERS = [
        ('youtube', 'YouTube'),
        ('linkedin', 'LinkedIn'),
        ('x', 'X'),
        ('spotify', 'Spotify'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    scopes = models.TextField(blank=True, null=True)
    provider_user_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'provider')


class Publication(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('uploading', 'Uploading'),
        ('live', 'Live'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=SocialToken.PROVIDERS)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    media_path = models.CharField(max_length=512)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    provider_post_id = models.CharField(max_length=255, blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)