import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import WeatherLog

REQUIRED_COLUMNS = {'date', 'temperature', 'humidity', 'soil_moisture'}

@login_required
def index(request):
    all_logs = WeatherLog.objects.order_by('-date')
    has_data = all_logs.exists()

    context = {'active': 'home', 'has_data': has_data}

    if has_data:
        latest = all_logs.first()
        recent_logs = list(all_logs[:7])
        chart_logs = list(reversed(recent_logs))  # oldest to newest for the chart

        context.update({
            'temperature': latest.temperature,
            'humidity': latest.humidity,
            'soil_moisture': latest.soil_moisture,
            'latest_date': latest.date,
            'chart_labels': [log.date.strftime('%b %d') for log in chart_logs],
            'chart_temperature': [log.temperature for log in chart_logs],
            'chart_humidity': [log.humidity for log in chart_logs],
            'chart_soil_moisture': [log.soil_moisture for log in chart_logs],
        })

    return render(request, 'home/index.html', context)


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