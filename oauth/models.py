# oauth/models.py
from django.db import models
from django.contrib.auth.models import User

class SocialToken(models.Model):
    PROVIDER_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('spotify', 'Spotify'),
        ('x', 'X'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="social_tokens",
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)

    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    scopes = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "provider")

    def __str__(self):
        return f"{self.user.username} – {self.provider}"


class Publication(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('uploading', 'Uploading'),
        ('live', 'Live'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=SocialToken.PROVIDER_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    media_path = models.CharField(max_length=512)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    provider_post_id = models.CharField(max_length=255, blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)