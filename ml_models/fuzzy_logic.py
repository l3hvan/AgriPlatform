"""
Fuzzy Logic irrigation & fertilizer advisor.

Unlike Random Forest or KNN, this isn't learned from historical data - it's an
expert rule system reacting to current conditions. The low/medium/high cutoffs
below are calibrated to the real range of soil moisture seen in the GLDAS data,
not arbitrary guesses.
"""
import numpy as np


def trimf(x, a, b, c):
    """Triangular membership function: 0 at a, peaks to 1 at b, back to 0 at c."""
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)


def soil_moisture_membership(x):
    return {
        'low': trimf(x, 71, 71, 200),
        'medium': trimf(x, 120, 200, 280),
        'high': trimf(x, 200, 446, 446),
    }


def temperature_membership(x):
    return {
        'low': trimf(x, 15, 15, 25),
        'medium': trimf(x, 20, 28, 36),
        'high': trimf(x, 30, 45, 45),
    }


def duration_membership(x):
    return {
        'short': trimf(x, 0, 0, 12),
        'medium': trimf(x, 5, 15, 25),
        'long': trimf(x, 18, 30, 30),
    }


def nutrient_membership(x):
    return {
        'low': trimf(x, 0, 0, 40),
        'medium': trimf(x, 25, 50, 75),
        'high': trimf(x, 60, 100, 100),
    }


# Rule base: IF soil_moisture IS x AND temperature IS y THEN irrigation_duration IS z
IRRIGATION_RULES = {
    ('low', 'low'): 'medium', ('low', 'medium'): 'long', ('low', 'high'): 'long',
    ('medium', 'low'): 'short', ('medium', 'medium'): 'medium', ('medium', 'high'): 'long',
    ('high', 'low'): 'short', ('high', 'medium'): 'short', ('high', 'high'): 'medium',
}

FERTILIZER_ACTIONS = {
    'low': 'Apply nitrogen now',
    'medium': 'Light application recommended',
    'high': 'No fertilizer needed',
}


def compute_irrigation(soil_moisture, temperature):
    """Fuzzify inputs -> apply rules -> aggregate -> defuzzify (centroid method)."""
    sm = soil_moisture_membership(soil_moisture)
    tm = temperature_membership(temperature)

    output_universe = np.arange(0, 30.5, 0.5)
    aggregated = np.zeros_like(output_universe)

    for (sm_label, t_label), out_label in IRRIGATION_RULES.items():
        strength = min(sm[sm_label], tm[t_label])  # AND = min
        if strength > 0:
            clipped = np.array([min(strength, duration_membership(x)[out_label]) for x in output_universe])
            aggregated = np.maximum(aggregated, clipped)  # aggregate = max

    if aggregated.sum() == 0:
        return 0.0
    return round((output_universe * aggregated).sum() / aggregated.sum(), 1)


def compute_fertilizer(nutrient_level):
    """Max-membership rule: whichever nutrient fuzzy set fits best wins."""
    memberships = nutrient_membership(nutrient_level)
    winning_label = max(memberships, key=memberships.get)
    return FERTILIZER_ACTIONS[winning_label]