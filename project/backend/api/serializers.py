from rest_framework import serializers
from .models import Country, RiskCategory, RiskData, RiskForecast, ReportRequest

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
    countries = serializers.ListField(child=serializers.CharField())
    risk_categories = serializers.ListField(child=serializers.CharField())
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    forecast_horizon = serializers.IntegerField(min_value=1, max_value=365)
    format = serializers.ChoiceField(choices=['pdf', 'docx'], default='pdf')