from django.shortcuts import render

def index(request):
    return render(request, 'grains_plants/index.html', {'active': 'grains-plants'})