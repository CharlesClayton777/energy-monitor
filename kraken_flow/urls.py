from django.contrib import admin
from django.urls import path

from meter_readings.api_views import (
    ReadingListView,
    ReadingsByDateView,
    MeterPointListView,
    MeterPointDetailView,
    FlowFileListView,
    StatsView,
    FileUploadView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/readings/', ReadingListView.as_view()),
    path('api/readings/by-date/', ReadingsByDateView.as_view()),
    path('api/meter-points/', MeterPointListView.as_view()),
    path('api/meter-points/<str:mpan>/', MeterPointDetailView.as_view()),
    path('api/files/', FlowFileListView.as_view()),
    path('api/stats/', StatsView.as_view()),
    path('api/upload/', FileUploadView.as_view()),
]