from django.urls import path
from .views import DashboardStatsView, ReportExportView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('export/', ReportExportView.as_view(), name='report-export'),
]