from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='grains-plants-index'),
    path('upload/', views.upload_seed_data, name='grains-plants-upload'),
]