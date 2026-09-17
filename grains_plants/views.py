import pandas as pd
import joblib
from django.conf import settings
from django.shortcuts import render
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

DISTRICTS = ['Banda', 'Chhatarpur', 'Cuddalore', 'Damoh', 'Datia', 'Jalaun',
             'Panna', 'Sagar', 'Thanjavur', 'Tikamgarh']

def index(request):
    selected_district = request.GET.get('district', 'Thanjavur')

    model_path = settings.BASE_DIR / 'ml_models' / 'trained'
    data_path = settings.BASE_DIR / 'ml_models' / 'datasets' / 'real_crop_data.csv'

    # Step 1: reuse the Random Forest to get the predicted crop for this district
    rf_model = joblib.load(model_path / 'random_forest_crop_model_real.pkl')
    district_encoder = joblib.load(model_path / 'district_encoder.pkl')

    data = pd.read_csv(data_path)
    latest = data.sort_values('year').groupby('district').tail(1).set_index('district')
    current = latest.loc[selected_district]

    rf_features = pd.DataFrame([{
        'district_encoded': district_encoder.transform([selected_district])[0],
        'NDVI_mean': current['NDVI_mean'],
        'groundwater_anomaly': current['groundwater_anomaly'],
    }])
    predicted_crop = rf_model.predict(rf_features)[0]

    # Step 2: KNN - find the 3 nearest OTHER seasons that also grew this crop,
    # and average their real yield as the estimate
    crop_rows = data[data['dominant_crop'] == predicted_crop].reset_index(drop=True)

    scaler = StandardScaler()
    X = scaler.fit_transform(crop_rows[['NDVI_mean', 'groundwater_anomaly']])
    query_X = scaler.transform(pd.DataFrame(
        [[current['NDVI_mean'], current['groundwater_anomaly']]],
        columns=['NDVI_mean', 'groundwater_anomaly']
    ))

    nn = NearestNeighbors(n_neighbors=min(4, len(crop_rows))).fit(X)
    distances, indices = nn.kneighbors(query_X)

    neighbors = crop_rows.iloc[indices[0]].copy()
    neighbors['distance'] = distances[0]
    neighbors = neighbors[~((neighbors['district'] == selected_district) & (neighbors['year'] == current['year']))]
    top3 = neighbors.head(3)

    estimated_yield = round(top3['yield_kg_per_ha'].mean() / 1000, 2)

    similar_seasons = []
    for _, row in top3.iterrows():
        similar_seasons.append({
            'district': row['district'],
            'year': int(row['year']),
            'yield_t_ha': round(row['yield_kg_per_ha'] / 1000, 2),
            'match_pct': round(100 / (1 + row['distance']), 1),
        })

    context = {
        'active': 'grains-plants',
        'districts': DISTRICTS,
        'selected_district': selected_district,
        'predicted_crop': predicted_crop,
        'estimated_yield': estimated_yield,
        'similar_seasons': similar_seasons,
    }
    return render(request, 'grains_plants/index.html', context)