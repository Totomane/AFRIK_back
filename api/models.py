from django.db import models
from django.contrib.auth.models import User
import json

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