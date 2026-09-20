import pandas as pd
import joblib
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import CropRecord

DISTRICTS = ['Banda', 'Chhatarpur', 'Cuddalore', 'Damoh', 'Datia', 'Jalaun',
             'Panna', 'Sagar', 'Thanjavur', 'Tikamgarh']

REQUIRED_COLUMNS = {'soil_type', 'rainfall_mm', 'temperature_c', 'humidity_percent'}

@login_required
def index(request):
    selected_district = request.GET.get('district', 'Thanjavur')

    model_path = settings.BASE_DIR / 'ml_models' / 'trained'
    model = joblib.load(model_path / 'random_forest_crop_model_real.pkl')
    district_encoder = joblib.load(model_path / 'district_encoder.pkl')

    data = pd.read_csv(settings.BASE_DIR / 'ml_models' / 'datasets' / 'real_crop_data.csv')
    latest = data.sort_values('year').groupby('district').tail(1).set_index('district')
    row = latest.loc[selected_district]

    features = pd.DataFrame([{
        'district_encoded': district_encoder.transform([selected_district])[0],
        'NDVI_mean': row['NDVI_mean'],
        'groundwater_anomaly': row['groundwater_anomaly'],
    }])

    prediction = model.predict(features)[0]
    confidence = round(max(model.predict_proba(features)[0]) * 100, 1)

    context = {
        'active': 'season-location',
        'districts': DISTRICTS,
        'selected_district': selected_district,
        'predicted_crop': prediction,
        'confidence': confidence,
        'data_year': int(row['year']),
    }
    return render(request, 'season_location/index.html', context)


@login_required
def upload_crop_data(request):
    if request.method != 'POST' or 'csv_file' not in request.FILES:
        messages.error(request, "No file was uploaded.")
        return redirect('season-location-index')

    uploaded_file = request.FILES['csv_file']

    if not uploaded_file.name.endswith('.csv'):
        messages.error(request, "Please upload a .csv file.")
        return redirect('season-location-index')

    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        messages.error(request, "Couldn't read that file - make sure it's a valid CSV.")
        return redirect('season-location-index')

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        messages.error(request, f"Missing required column(s): {', '.join(sorted(missing))}")
        return redirect('season-location-index')

    records = [
        CropRecord(
            soil_type=row['soil_type'],
            rainfall_mm=row['rainfall_mm'],
            temperature_c=row['temperature_c'],
            humidity_percent=row['humidity_percent'],
            uploaded_by=request.user,
        )
        for _, row in df.iterrows()
    ]
    CropRecord.objects.bulk_create(records)
    messages.success(request, f"Uploaded {len(records)} crop data row(s) successfully.")
    return redirect('season-location-index')