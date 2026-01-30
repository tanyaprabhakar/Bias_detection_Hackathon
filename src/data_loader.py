# src/data_loader.py
import pandas as pd

def load_dataset(uploaded_file):
    """Load CSV or Excel dataset into a DataFrame"""
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    return df

def analyze_columns(df, max_unique=10):
    """
    Returns:
    - eligible_sensitive: list of valid sensitive attributes
    - excluded_columns: dict of excluded attributes with reasons
    """
    eligible_sensitive = []
    excluded_columns = {}

    for col in df.columns:
        # Check if identifier-like
        if df[col].nunique() / len(df) > 0.9:
            excluded_columns[col] = "Unique identifier"
        # Check if numeric
        elif df[col].dtype != "object" and df[col].dtype.name != "category":
            excluded_columns[col] = "Numeric attribute"
        # Check if too many categories
        elif df[col].nunique() > max_unique:
            excluded_columns[col] = "Too many categories"
        else:
            eligible_sensitive.append(col)

    return eligible_sensitive, excluded_columns