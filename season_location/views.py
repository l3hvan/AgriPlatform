from django.shortcuts import render

def index(request):
    return render(request, 'season_location/index.html', {'active': 'season-location'})