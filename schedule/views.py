import pandas as pd
from django.conf import settings
from django.shortcuts import render
from ml_models.fuzzy_logic import compute_irrigation, compute_fertilizer

DISTRICTS = ['Banda', 'Chhatarpur', 'Cuddalore', 'Damoh', 'Datia', 'Jalaun',
             'Panna', 'Sagar', 'Thanjavur', 'Tikamgarh']

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