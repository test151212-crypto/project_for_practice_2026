from rest_framework import serializers
from .models import CrawlerSource, CrawlerLog

class CrawlerSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlerSource
        fields = '__all__'
        read_only_fields = ('last_run', 'created_at')

class CrawlerLogSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)

    class Meta:
        model = CrawlerLog
        fields = '__all__'