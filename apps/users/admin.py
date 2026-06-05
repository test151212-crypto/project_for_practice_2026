from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FreelancerProfile, CustomerProfile

admin.site.register(User, UserAdmin)
admin.site.register(FreelancerProfile)
admin.site.register(CustomerProfile)