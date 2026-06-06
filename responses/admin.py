from django.contrib import admin
from .models import Response, Review, Complaint

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'freelancer', 'status', 'sent_at')
    list_filter = ('status',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'author', 'target', 'rating', 'created_at')
    list_filter = ('rating',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'complaint_type', 'object_id', 'created_by', 'resolved', 'created_at')
    list_filter = ('complaint_type', 'resolved')