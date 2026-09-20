import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import WeatherLog

REQUIRED_COLUMNS = {'date', 'temperature', 'humidity', 'soil_moisture'}

@login_required
def index(request):
    return render(request, 'home/index.html', {'active': 'home'})

@login_required
def upload_weather_log(request):
    if request.method != 'POST' or 'csv_file' not in request.FILES:
        messages.error(request, "No file was uploaded.")
        return redirect('home-index')

    uploaded_file = request.FILES['csv_file']

    if not uploaded_file.name.endswith('.csv'):
        messages.error(request, "Please upload a .csv file.")
        return redirect('home-index')

    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        messages.error(request, "Couldn't read that file - make sure it's a valid CSV.")
        return redirect('home-index')

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        messages.error(request, f"Missing required column(s): {', '.join(sorted(missing))}")
        return redirect('home-index')

    logs = [
        WeatherLog(
            date=row['date'],
            temperature=row['temperature'],
            humidity=row['humidity'],
            soil_moisture=row['soil_moisture'],
            uploaded_by=request.user,
        )
        for _, row in df.iterrows()
    ]
    WeatherLog.objects.bulk_create(logs)
    messages.success(request, f"Uploaded {len(logs)} weather log row(s) successfully.")
    return redirect('home-index')