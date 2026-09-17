import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

# Load the same merged dataset used by Random Forest, now with real yield values added
df = pd.read_csv('ml_models/datasets/real_crop_data.csv')

# Leave-one-out validation: for every district-year, estimate its yield using the
# 3 nearest OTHER same-crop seasons, then compare to what actually happened.
# This tells us how trustworthy the approach is - same idea as Random Forest's
# test accuracy, just measured as error instead of correctness.
errors = []
for crop in df['dominant_crop'].unique():
    crop_rows = df[df['dominant_crop'] == crop].reset_index(drop=True)
    if len(crop_rows) < 5:
        continue  # too few real examples to meaningfully evaluate this crop

    scaler = StandardScaler()
    X = scaler.fit_transform(crop_rows[['NDVI_mean', 'groundwater_anomaly']])
    nn = NearestNeighbors(n_neighbors=4).fit(X)  # 4 so we can drop self and keep 3
    distances, indices = nn.kneighbors(X)

    for i in range(len(crop_rows)):
        neighbor_idx = [j for j in indices[i] if j != i][:3]
        estimated = crop_rows.iloc[neighbor_idx]['yield_kg_per_ha'].mean()
        actual = crop_rows.iloc[i]['yield_kg_per_ha']
        pct_error = abs(estimated - actual) / actual * 100
        errors.append({'crop': crop, 'pct_error': pct_error})

results = pd.DataFrame(errors)
print("Mean absolute % error by crop:")
print(results.groupby('crop')['pct_error'].agg(['mean', 'count']))
print(f"\nOverall mean absolute % error: {results['pct_error'].mean():.1f}%")