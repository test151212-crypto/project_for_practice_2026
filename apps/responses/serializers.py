from rest_framework import serializers
from .models import Response, Review, Complaint

class ResponseSerializer(serializers.ModelSerializer):
    freelancer_name = serializers.CharField(source='freelancer.username', read_only=True)
    order_title = serializers.CharField(source='order.title', read_only=True)

    class Meta:
        model = Response
        fields = '__all__'
        read_only_fields = ('freelancer', 'status', 'sent_at', 'viewed_at')

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('author', 'created_at')

class ComplaintSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')