from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home-index'),
    path('upload/', views.upload_weather_log, name='home-upload'),
]