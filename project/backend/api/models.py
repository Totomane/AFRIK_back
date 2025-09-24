from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum
import json
import uuid
import os

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    iso_code = models.CharField(max_length=3, unique=True)
    region = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class RiskCategory(models.Model):
    RISK_TYPES = [
        ('climate', 'Climate Change'),
        ('cyber', 'Cyber Security'),
        ('financial', 'Financial Crisis'),
        ('geopolitical', 'Geopolitical Tensions'),
        ('pandemic', 'Pandemic Outbreak'),
        ('supply-chain', 'Supply Chain Disruption'),
        ('energy', 'Energy Crisis'),
        ('water', 'Water Scarcity'),
        ('food', 'Food Security'),
        ('migration', 'Mass Migration'),
        ('terrorism', 'Terrorism'),
        ('natural-disaster', 'Natural Disasters'),
        ('economic', 'Economic Recession'),
        ('technology', 'Technology Disruption'),
        ('social', 'Social Unrest'),
    ]
    
    risk_type = models.CharField(max_length=50, choices=RISK_TYPES, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_risk_type_display()

class RiskData(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    risk_category = models.ForeignKey(RiskCategory, on_delete=models.CASCADE)
    date = models.DateField()
    risk_level = models.FloatField()  # 0-1 scale
    confidence_score = models.FloatField()  # 0-1 scale
    source = models.CharField(max_length=200)
    raw_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['country', 'risk_category', 'date', 'source']
    
    def __str__(self):
        return f"{self.country.name} - {self.risk_category.risk_type} - {self.date}"

class RiskForecast(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    risk_category = models.ForeignKey(RiskCategory, on_delete=models.CASCADE)
    forecast_date = models.DateField()
    predicted_risk_level = models.FloatField()
    confidence_interval_lower = models.FloatField()
    confidence_interval_upper = models.FloatField()
    model_used = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['country', 'risk_category', 'forecast_date', 'model_used']

class ReportRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    countries = models.ManyToManyField(Country)
    risk_categories = models.ManyToManyField(RiskCategory)
    start_date = models.DateField()
    end_date = models.DateField()
    forecast_horizon = models.IntegerField()  # days
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=500, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Report {self.id} - {self.status}"


def user_media_upload_path(instance, filename):
    """Generate upload path: media/users/{user_id}/{uuid}_{filename}"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"users/{instance.owner.id}/{filename}"


class UserProfile(models.Model):
    """Extended user profile for storage quotas"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    storage_quota_mb = models.PositiveIntegerField(
        default=settings.DEFAULT_USER_STORAGE_QUOTA,
        help_text="Storage quota in MB"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.storage_quota_mb}MB"
    
    def get_used_storage_mb(self):
        """Calculate total used storage in MB"""
        total_bytes = self.user.mediafile_set.aggregate(
            total=Sum('file_size')
        )['total'] or 0
        return round(total_bytes / (1024 * 1024), 2)
    
    def get_remaining_storage_mb(self):
        """Calculate remaining storage in MB"""
        return max(0, self.storage_quota_mb - self.get_used_storage_mb())
    
    def can_upload(self, file_size_bytes):
        """Check if user can upload a file of given size"""
        file_size_mb = file_size_bytes / (1024 * 1024)
        return file_size_mb <= self.get_remaining_storage_mb()


class MediaFile(models.Model):
    """Per-user media file storage with metadata"""
    FILE_TYPES = [
        ('pdf', 'PDF Report'),
        ('mp3', 'Audio Podcast'),
        ('txt', 'Text File'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_media_upload_path, blank=True, null=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    original_filename = models.CharField(max_length=255)
    
    # Generation parameters
    countries = models.JSONField(default=list, blank=True)
    risk_categories = models.JSONField(default=list, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    generation_params = models.JSONField(default=dict, blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_message = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    accessed_at = models.DateTimeField(auto_now=True)
    
    # Content metadata
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['owner', 'file_type']),
            models.Index(fields=['owner', 'generated_at']),
        ]
    
    def __str__(self):
        return f"{self.owner.username} - {self.original_filename} ({self.file_type})"
    
    def get_file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    def get_presigned_url(self, expires_in=3600):
        """Generate presigned URL for R2 storage"""
        if not self.file:
            return None
            
        if hasattr(self.file.storage, 'url'):
            # For R2/S3 storage, generate presigned URL
            try:
                from botocore.exceptions import ClientError
                import boto3
                from django.conf import settings
                
                if not settings.USE_R2_STORAGE:
                    return self.file.url
                
                s3_client = boto3.client(
                    's3',
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )
                
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                        'Key': self.file.name
                    },
                    ExpiresIn=expires_in
                )
                return presigned_url
                
            except (ClientError, Exception) as e:
                print(f"Error generating presigned URL: {e}")
                return self.file.url
        
        return self.file.url if self.file else None