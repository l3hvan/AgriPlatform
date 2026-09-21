import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ml_models.fuzzy_logic import compute_irrigation, compute_fertilizer
from .models import SensorReading

DISTRICTS = ['Banda', 'Chhatarpur', 'Cuddalore', 'Damoh', 'Datia', 'Jalaun',
             'Panna', 'Sagar', 'Thanjavur', 'Tikamgarh']

REQUIRED_COLUMNS = {'district', 'soil_moisture', 'temperature', 'nutrient_level'}

@login_required
def index(request):
    selected_district = request.GET.get('district', 'Thanjavur')
    temperature = float(request.GET.get('temperature', 28))
    nutrient_level = float(request.GET.get('nutrient_level', 50))

    lookup = pd.read_csv(settings.BASE_DIR / 'ml_models' / 'datasets' / 'soil_moisture_lookup.csv')
    soil_moisture = lookup[lookup['district'] == selected_district]['soil_moisture'].iloc[0]

    irrigation_minutes = compute_irrigation(soil_moisture, temperature)
    fertilizer_action = compute_fertilizer(nutrient_level)

    context = {
        'active': 'schedule',
        'districts': DISTRICTS,
        'selected_district': selected_district,
        'soil_moisture': round(soil_moisture, 1),
        'temperature': temperature,
        'nutrient_level': nutrient_level,
        'irrigation_minutes': irrigation_minutes,
        'fertilizer_action': fertilizer_action,
    }
    return render(request, 'schedule/index.html', context)


@login_required
def upload_sensor_data(request):
    if request.method != 'POST' or 'csv_file' not in request.FILES:
        messages.error(request, "No file was uploaded.")
        return redirect('schedule-index')

    uploaded_file = request.FILES['csv_file']

    if not uploaded_file.name.endswith('.csv'):
        messages.error(request, "Please upload a .csv file.")
        return redirect('schedule-index')

    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        messages.error(request, "Couldn't read that file - make sure it's a valid CSV.")
        return redirect('schedule-index')

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        messages.error(request, f"Missing required column(s): {', '.join(sorted(missing))}")
        return redirect('schedule-index')

    readings = [
        SensorReading(
            district=row['district'],
            soil_moisture=row['soil_moisture'],
            temperature=row['temperature'],
            nutrient_level=row['nutrient_level'],
            uploaded_by=request.user,
        )
        for _, row in df.iterrows()
    ]
    SensorReading.objects.bulk_create(readings)
    messages.success(request, f"Uploaded {len(readings)} sensor reading(s) successfully.")
    return redirect('schedule-index')