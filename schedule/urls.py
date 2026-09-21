from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='schedule-index'),
    path('upload/', views.upload_sensor_data, name='schedule-upload'),
]