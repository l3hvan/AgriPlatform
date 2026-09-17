import pandas as pd
import joblib
from django.conf import settings
from django.shortcuts import render

DISTRICTS = ['Banda', 'Chhatarpur', 'Cuddalore', 'Damoh', 'Datia', 'Jalaun',
             'Panna', 'Sagar', 'Thanjavur', 'Tikamgarh']

def index(request):
    selected_district = request.GET.get('district', 'Thanjavur')

    model_path = settings.BASE_DIR / 'ml_models' / 'trained'
    model = joblib.load(model_path / 'random_forest_crop_model_real.pkl')
    district_encoder = joblib.load(model_path / 'district_encoder.pkl')

    # Look up this district's most recent known satellite readings
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