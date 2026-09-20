from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='season-location-index'),
    path('upload/', views.upload_crop_data, name='season-location-upload'),
]