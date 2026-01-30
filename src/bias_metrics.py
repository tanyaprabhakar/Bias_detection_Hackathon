# src/bias_metrics.py
import pandas as pd
import numpy as np

def representation_and_sampling_bias(df, sensitive_attr):
    """Calculate representation bias"""
    total = len(df)
    counts = df[sensitive_attr].value_counts(dropna=False)
    proportions = counts / total

    rep_df = pd.DataFrame({
        "group": counts.index.astype(str),
        "count": counts.values,
        "proportion": proportions.round(3).values
    })

    min_proportion = proportions.min()
    return rep_df, round(min_proportion, 3)

def label_bias(df, sensitive_attr, target_attr, positive_label):
    """Calculate label bias"""
    rates = []

    for group in df[sensitive_attr].dropna().unique():
        group_df = df[df[sensitive_attr] == group]
        rate = (group_df[target_attr] == positive_label).mean()
        rates.append(rate)

    label_diff = max(rates) - min(rates) if len(rates) > 1 else 0
    return round(label_diff, 3)

def historical_bias(df, sensitive_attr, target_attr, positive_label):
    """Calculate historical bias"""
    outcomes = []

    for group in df[sensitive_attr].dropna().unique():
        group_df = df[df[sensitive_attr] == group]
        rate = (group_df[target_attr] == positive_label).mean()
        outcomes.append(rate)

    hist_diff = max(outcomes) - min(outcomes) if len(outcomes) > 1 else 0
    return round(hist_diff, 3)

def statistical_parity_difference(df, sensitive_attr, target_attr, positive_label, reference_group):
    """Calculate statistical parity difference"""
    ref_rate = (df[df[sensitive_attr] == reference_group][target_attr] == positive_label).mean()
    spd_vals = []

    for group in df[sensitive_attr].dropna().unique():
        group_rate = (df[df[sensitive_attr] == group][target_attr] == positive_label).mean()
        spd_vals.append(group_rate - ref_rate)

    max_spd = max(abs(v) for v in spd_vals) if spd_vals else 0
    return round(max_spd, 3)

def disparate_impact(df, sensitive_attr, target_attr, positive_label, reference_group):
    """Calculate disparate impact"""
    ref_rate = (df[df[sensitive_attr] == reference_group][target_attr] == positive_label).mean()
    deviations = []

    for group in df[sensitive_attr].dropna().unique():
        group_rate = (df[df[sensitive_attr] == group][target_attr] == positive_label).mean()
        if ref_rate > 0:
            deviations.append(abs(1 - (group_rate / ref_rate)))

    max_di_dev = max(deviations) if deviations else 0
    return round(max_di_dev, 3)

def final_bias_verdict(min_representation, label_diff, historical_diff, max_spd, max_di_deviation):
    """Aggregates all supervised bias signals"""
    rep_score = max(0, (0.5 - min_representation) / 0.5)
    label_score = min(label_diff / 0.3, 1.0)
    hist_score = min(historical_diff / 0.3, 1.0)
    spd_score = min(max_spd / 0.3, 1.0)
    di_score = min(max_di_deviation / 0.5, 1.0)

    outcome_severity = max(label_score, hist_score, spd_score, di_score)
    severity = max(outcome_severity, rep_score)

    bias_percentage = int(severity * 100)

    if bias_percentage >= 60:
        verdict = "BIASED"
        reason = "Severe outcome-based disparity detected across groups."
    elif bias_percentage >= 30:
        verdict = "POTENTIALLY BIASED"
        reason = "Some disparity detected. Further investigation recommended."
    else:
        verdict = "NOT BIASED"
        reason = "No significant bias detected."

    return {
        "verdict": verdict,
        "bias_percentage": bias_percentage,
        "reason": reason
    }

def unsupervised_bias_verdict(min_representation):
    """Unsupervised bias detection"""
    if min_representation < 0.3:
        verdict = "HIGH RISK OF REPRESENTATION BIAS"
    elif min_representation < 0.4:
        verdict = "POTENTIAL REPRESENTATION BIAS"
    else:
        verdict = "NO DIRECT EVIDENCE OF BIAS (UNSUPERVISED)"

    bias_percentage = int((0.5 - min_representation) / 0.5 * 100)
    bias_percentage = max(0, min(bias_percentage, 100))

    return {
        "verdict": verdict,
        "bias_percentage": bias_percentage,
        "reason": "Assessment based solely on group representation. Outcome fairness cannot be evaluated without labels."
    }