from functools import lru_cache

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ml_models.evaluate_models import DATA_PATH, evaluate_fuzzy, evaluate_knn, evaluate_random_forest
from .models import WeatherLog

REQUIRED_COLUMNS = {'date', 'temperature', 'humidity', 'soil_moisture'}


@lru_cache(maxsize=1)
def model_evaluation():
    """Cross-validation takes a second or two, and the dataset only changes on redeploy - compute once."""
    df = pd.read_csv(DATA_PATH)
    rf = evaluate_random_forest(df)
    knn = evaluate_knn(df)
    fuzzy = evaluate_fuzzy()

    return {
        'rf': {
            'holdout_accuracy': round(rf['holdout_accuracy'] * 100, 1),
            'cv_accuracy': round(rf['cv_accuracy'] * 100, 1),
            'cv_std': round(rf['cv_std'] * 100, 1),
            'baseline_accuracy': round(rf['baseline_accuracy'] * 100, 1),
            'baseline_crop': rf['baseline_crop'],
            'crop_counts': df['dominant_crop'].value_counts().to_dict(),
            'rows': len(df),
        },
        'knn': {
            'overall_error': round(knn['overall_error'], 1),
            'overall_accuracy': round(100 - knn['overall_error'], 1),
            'by_crop': [
                {'crop': crop, 'error': round(row['mean'], 1), 'count': int(row['count'])}
                for crop, row in knn['by_crop'].iterrows()
            ],
        },
        'fuzzy': {
            'temperatures': list(fuzzy['sweep'].columns),
            'sweep': [
                {'label': label, 'values': [round(v, 1) for v in row]}
                for label, row in fuzzy['sweep'].iterrows()
            ],
            'checks': [{'name': name, 'passed': bool(passed)} for name, passed in fuzzy['checks'].items()],
            'checks_passed': sum(bool(p) for p in fuzzy['checks'].values()),
            'checks_total': len(fuzzy['checks']),
        },
    }


@login_required
def models_overview(request):
    context = {'active': 'models', **model_evaluation()}
    return render(request, 'home/models.html', context)

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