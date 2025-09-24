from rest_framework import serializers
from .models import Country, RiskCategory, RiskData, RiskForecast, ReportRequest, MediaFile, UserProfile
from django.contrib.auth.models import User

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class RiskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskCategory
        fields = '__all__'

class RiskDataSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    risk_type = serializers.CharField(source='risk_category.risk_type', read_only=True)
    
    class Meta:
        model = RiskData
        fields = '__all__'

class RiskForecastSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    risk_type = serializers.CharField(source='risk_category.risk_type', read_only=True)
    
    class Meta:
        model = RiskForecast
        fields = '__all__'

class ReportRequestSerializer(serializers.ModelSerializer):
    countries_data = CountrySerializer(source='countries', many=True, read_only=True)
    risk_categories_data = RiskCategorySerializer(source='risk_categories', many=True, read_only=True)
    
    class Meta:
        model = ReportRequest
        fields = '__all__'

class ReportGenerationSerializer(serializers.Serializer):
    country = serializers.CharField()                  # "France"
    risks = serializers.ListField(child=serializers.CharField())  # ["R1", "R2"]
    year = serializers.IntegerField()                 # 2026
    format = serializers.ChoiceField(choices=["pdf", "docx"], default="pdf")


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    used_storage_mb = serializers.SerializerMethodField()
    remaining_storage_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['storage_quota_mb', 'username', 'used_storage_mb', 'remaining_storage_mb', 'created_at']
        read_only_fields = ['created_at']
    
    def get_used_storage_mb(self, obj):
        return obj.get_used_storage_mb()
    
    def get_remaining_storage_mb(self, obj):
        return obj.get_remaining_storage_mb()


class MediaFileSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFile
        fields = [
            'id', 'owner_username', 'file_type', 'file_size', 'file_size_mb',
            'original_filename', 'countries', 'risk_categories', 'year',
            'status', 'error_message', 'generated_at', 'accessed_at',
            'title', 'description', 'tags', 'download_url'
        ]
        read_only_fields = [
            'id', 'owner_username', 'file_size', 'file_size_mb',
            'generated_at', 'accessed_at', 'download_url'
        ]
    
    def get_file_size_mb(self, obj):
        return obj.get_file_size_mb()
    
    def get_download_url(self, obj):
        return obj.get_presigned_url()


class GeneratePDFSerializer(serializers.Serializer):
    countries = serializers.ListField(child=serializers.CharField())
    risks = serializers.ListField(child=serializers.CharField())
    year = serializers.IntegerField()
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)


class GeneratePodcastSerializer(serializers.Serializer):
    countries = serializers.ListField(child=serializers.CharField())
    risks = serializers.ListField(child=serializers.CharField())
    year = serializers.IntegerField()
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    tone = serializers.CharField(default='serious') 