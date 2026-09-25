"""
One-stop accuracy report for all three pieces of logic the app uses.

Run from the project root:  python ml_models/evaluate_models.py

Unlike the train_* scripts, this does NOT overwrite any saved .pkl models -
it only measures how well each approach performs.
"""
import os
import sys
import warnings

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder, StandardScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_models.fuzzy_logic import compute_fertilizer, compute_irrigation

# Rare crops have fewer rows than CV folds - sklearn warns, but the score is still valid
warnings.filterwarnings('ignore', category=UserWarning)

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets', 'real_crop_data.csv')


def evaluate_random_forest(df):
    """Crop recommendation (used by Season & Location and Grains & Plants)."""
    df = df.copy()
    df['district_encoded'] = LabelEncoder().fit_transform(df['district'])
    X = df[['district_encoded', 'NDVI_mean', 'groundwater_anomaly']]
    y = df['dominant_crop']

    # Same 80/20 split as train_random_forest_real.py, so the numbers match
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=100, random_state=42).fit(X_train, y_train)
    predictions = model.predict(X_test)

    # Cross-validation averages over 5 different splits - steadier than one split on 110 rows
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(RandomForestClassifier(n_estimators=100, random_state=42), X, y, cv=cv)

    # Baseline: always guessing the most common crop. The model must beat this to be useful.
    baseline = y.value_counts(normalize=True).iloc[0]

    return {
        'holdout_accuracy': accuracy_score(y_test, predictions),
        'cv_accuracy': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'baseline_accuracy': baseline,
        'baseline_crop': y.value_counts().index[0],
        'report': classification_report(y_test, predictions, zero_division=0),
    }


def evaluate_knn(df):
    """Yield estimate (Grains & Plants). Leave-one-out: predict each season from its 3 nearest others."""
    errors = []
    for crop in df['dominant_crop'].unique():
        crop_rows = df[df['dominant_crop'] == crop].reset_index(drop=True)
        if len(crop_rows) < 5:
            continue  # too few real examples to meaningfully evaluate this crop

        X = StandardScaler().fit_transform(crop_rows[['NDVI_mean', 'groundwater_anomaly']])
        _, indices = NearestNeighbors(n_neighbors=4).fit(X).kneighbors(X)  # 4 so we can drop self and keep 3

        for i in range(len(crop_rows)):
            neighbor_idx = [j for j in indices[i] if j != i][:3]
            estimated = crop_rows.iloc[neighbor_idx]['yield_kg_per_ha'].mean()
            actual = crop_rows.iloc[i]['yield_kg_per_ha']
            errors.append({'crop': crop, 'pct_error': abs(estimated - actual) / actual * 100})

    results = pd.DataFrame(errors)
    by_crop = results.groupby('crop')['pct_error'].agg(['mean', 'count']).sort_values('mean')
    return {'by_crop': by_crop, 'overall_error': results['pct_error'].mean()}


def evaluate_fuzzy():
    """Irrigation & fertilizer (Schedule). No ground truth exists, so check the rules behave sensibly."""
    moistures = [71, 150, 200, 300, 446]
    temperatures = [15, 22, 28, 36, 45]
    sweep = pd.DataFrame(
        [[float(compute_irrigation(sm, t)) for t in temperatures] for sm in moistures],
        index=[f'moisture {sm}' for sm in moistures],
        columns=[f'{t}C' for t in temperatures],
    )

    checks = {
        'Never recommends 0 minutes inside the calibrated range': (sweep.values > 0).all(),
        'Dry soil always gets more water than wet soil': (sweep.iloc[0] > sweep.iloc[-1]).all(),
        'Hottest day always gets more water than coolest day': (sweep.iloc[:, -1] > sweep.iloc[:, 0]).all(),
        'Low nutrients -> apply nitrogen': compute_fertilizer(10) == 'Apply nitrogen now',
        'High nutrients -> no fertilizer': compute_fertilizer(90) == 'No fertilizer needed',
    }
    return {'sweep': sweep, 'checks': checks}


def main():
    df = pd.read_csv(DATA_PATH)

    print('=' * 60)
    print('1. RANDOM FOREST - crop recommendation')
    print('=' * 60)
    rf = evaluate_random_forest(df)
    print(f"Test accuracy (20% held back):  {rf['holdout_accuracy'] * 100:.1f}%")
    print(f"5-fold cross-validation:        {rf['cv_accuracy'] * 100:.1f}% (+/- {rf['cv_std'] * 100:.1f}%)")
    print(f"Baseline (always '{rf['baseline_crop']}'):   {rf['baseline_accuracy'] * 100:.1f}%")
    print('\nPer-crop results on the test split:')
    print(rf['report'])

    print('=' * 60)
    print('2. KNN - yield estimate (leave-one-out)')
    print('=' * 60)
    knn = evaluate_knn(df)
    print('Mean absolute % error by crop:')
    print(knn['by_crop'].round(1).to_string())
    print(f"\nOverall mean absolute % error: {knn['overall_error']:.1f}%")
    print(f"(i.e. roughly {100 - knn['overall_error']:.0f}% accurate on average)\n")

    print('=' * 60)
    print('3. FUZZY LOGIC - irrigation minutes & fertilizer')
    print('=' * 60)
    fuzzy = evaluate_fuzzy()
    print('Irrigation minutes (soil moisture x temperature):')
    print(fuzzy['sweep'].to_string())
    print('\nBehaviour checks:')
    for name, passed in fuzzy['checks'].items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")


if __name__ == '__main__':
    main()
