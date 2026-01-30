# src/mitigation.py

def diagnose_bias_and_recommend_fixes(
    min_representation,
    label_diff,
    historical_diff,
    max_spd,
    max_di_deviation
):
    """
    Diagnoses bias types based on metric thresholds
    and suggests mitigation strategies.
    
    IMPORTANT:
    - Does NOT modify the dataset
    - Only provides recommendations
    """

    bias_types = []
    fixes = {}

    # -------------------------------
    # Representation / Sampling Bias
    # -------------------------------
    if min_representation < 0.4:
        bias_types.append("Representation Bias")
        fixes["Representation Bias"] = [
            "Collect more data for underrepresented groups",
            "Use stratified sampling during data collection",
            "Apply re-weighting during model training (not data duplication)"
        ]

    # -------------------------------
    # Label Bias
    # -------------------------------
    if label_diff > 0.2:
        bias_types.append("Label Bias")
        fixes["Label Bias"] = [
            "Audit labeling process for human or systemic bias",
            "Use blind or multi-annotator labeling",
            "Apply label smoothing or re-weighting during training"
        ]

    # -------------------------------
    # Historical Bias
    # -------------------------------
    if historical_diff > 0.2:
        bias_types.append("Historical Bias")
        fixes["Historical Bias"] = [
            "Incorporate fairness constraints during model training",
            "Use counterfactual fairness techniques",
            "Add post-processing fairness adjustments"
        ]

    # -------------------------------
    # Outcome / Statistical Bias
    # -------------------------------
    if max_spd > 0.1 or max_di_deviation > 0.2:
        bias_types.append("Outcome Bias")
        fixes["Outcome Bias"] = [
            "Use fairness-aware algorithms (e.g., Fairlearn)",
            "Apply threshold optimization per group",
            "Use post-processing methods like equalized odds"
        ]

    if not bias_types:
        bias_types.append("No Significant Bias Detected")
        fixes["No Significant Bias Detected"] = [
            "Continue monitoring bias over time",
            "Validate fairness after model training"
        ]

    return bias_types, fixes