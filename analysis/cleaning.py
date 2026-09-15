"""
Data Cleaning and Preprocessing Module for UCI Heart Disease Dataset.
Handles loading, schema validation, type normalization, categorical mapping, and multi-variable filtering.
"""

import os
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np

# Canonical dataset schema expected for UCI Cleveland dataset
CANONICAL_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", 
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"
]

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "heart_disease.csv")

# Human-readable categorical label mappings
SEX_MAP = {0: "Female", 1: "Male"}

# UCI standard CP: 1=typical angina, 2=atypical angina, 3=non-anginal pain, 4=asymptomatic
# Also accounts for 0-indexed variations (0, 1, 2, 3) if encountered
CP_MAP_1_BASED = {
    1: "Typical Angina",
    2: "Atypical Angina",
    3: "Non-Anginal Pain",
    4: "Asymptomatic"
}
CP_MAP_0_BASED = {
    0: "Typical Angina",
    1: "Atypical Angina",
    2: "Non-Anginal Pain",
    3: "Asymptomatic"
}

FBS_MAP = {0: "≤ 120 mg/dl", 1: "> 120 mg/dl"}

RESTECG_MAP = {
    0: "Normal",
    1: "ST-T Abnormality",
    2: "LV Hypertrophy"
}

EXANG_MAP = {0: "No", 1: "Yes"}

SLOPE_MAP_1_BASED = {
    1: "Upsloping",
    2: "Flat",
    3: "Downsloping"
}
SLOPE_MAP_0_BASED = {
    0: "Upsloping",
    1: "Flat",
    2: "Downsloping"
}

THAL_MAP = {
    3: "Normal",
    6: "Fixed Defect",
    7: "Reversible Defect",
    # 1-indexed alternate encoding
    1: "Normal",
    2: "Fixed Defect"
}


def assign_age_group(age: float) -> str:
    """Categorize age into demographic analytical cohorts."""
    if pd.isna(age):
        return "Unknown"
    if age < 40:
        return "<40"
    elif 40 <= age <= 49:
        return "40-49"
    elif 50 <= age <= 59:
        return "50-59"
    elif 60 <= age <= 69:
        return "60-69"
    else:
        return "70+"


def load_and_clean_data(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load, validate, clean, and enrich the UCI Heart Disease dataset.
    
    Cleaning Decisions:
    1. Schema Validation: Checks for the presence of the 14 standard attributes.
    2. Missing Values: Replaces '?', empty strings, and whitespace with NaN.
       For descriptive analysis, numerical records are cast properly.
       Records with null values in ca (4) and thal (2) are retained for non-ca/thal analyses
       to avoid discarding 6 otherwise complete clinical records.
    3. Target Normalization: Binarizes target into target_binary (0 = No Disease, 1 = Disease for target >= 1).
    4. Categorical Labeling: Creates explicit human-readable string columns (e.g. sex_label, cp_label, outcome_label).
    5. Cohort Generation: Adds age_group column for demographic distribution analysis.
    """
    path = file_path or DEFAULT_DATA_PATH
    
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at expected path: '{path}'. "
            "Please ensure 'heart_disease.csv' is placed inside the 'data/' directory."
        )
    
    # Load dataset treating '?' and whitespace as missing
    try:
        df = pd.read_csv(
            path,
            na_values=["?", "NA", "N/A", "null", "", " "],
            skipinitialspace=True
        )
    except Exception as exc:
        raise ValueError(f"Failed to parse dataset at '{path}': {str(exc)}")
    
    # Normalize column names (lowercase, strip whitespace, replace spaces with underscores)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    
    # Check for target alias (some datasets name it 'num' or 'condition' or 'diagnosis')
    rename_dict = {}
    if "num" in df.columns and "target" not in df.columns:
        rename_dict["num"] = "target"
    elif "condition" in df.columns and "target" not in df.columns:
        rename_dict["condition"] = "target"
    if rename_dict:
        df.rename(columns=rename_dict, inplace=True)
        
    # Schema check
    missing_cols = [c for c in CANONICAL_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Dataset schema mismatch! Missing required canonical columns: {missing_cols}. "
            f"Found columns: {list(df.columns)}"
        )
    
    # Coerce numeric types
    for col in CANONICAL_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    # Target normalization (0 -> No Disease, >= 1 -> Disease)
    # Store original target in target_raw
    df["target_raw"] = df["target"].copy()
    df["target_binary"] = (df["target"] >= 1).astype(int)
    df["outcome_label"] = df["target_binary"].map({0: "No Disease", 1: "Disease"})
    
    # Detect CP scale (1-4 vs 0-3)
    cp_unique = set(df["cp"].dropna().unique())
    if 4 in cp_unique or 4.0 in cp_unique:
        cp_map = CP_MAP_1_BASED
    else:
        cp_map = CP_MAP_0_BASED
    df["cp_label"] = df["cp"].map(cp_map).fillna("Unknown")
    
    # Map other categoricals
    df["sex_label"] = df["sex"].map(SEX_MAP).fillna("Unknown")
    df["fbs_label"] = df["fbs"].map(FBS_MAP).fillna("Unknown")
    df["restecg_label"] = df["restecg"].map(RESTECG_MAP).fillna("Unknown")
    df["exang_label"] = df["exang"].map(EXANG_MAP).fillna("Unknown")
    
    slope_unique = set(df["slope"].dropna().unique())
    slope_map = SLOPE_MAP_1_BASED if 3 in slope_unique or 3.0 in slope_unique else SLOPE_MAP_0_BASED
    df["slope_label"] = df["slope"].map(slope_map).fillna("Unknown")
    
    df["thal_label"] = df["thal"].map(THAL_MAP).fillna("Unknown")
    
    # Demographic cohorts
    df["age_group"] = df["age"].apply(assign_age_group)
    
    # Assign unique patient record index
    df["patient_id"] = np.arange(1, len(df) + 1)
    
    return df


def filter_dataframe(
    df: pd.DataFrame,
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    outcome: Optional[str] = None,
    cp: Optional[str] = None
) -> pd.DataFrame:
    """
    Apply multi-attribute filter criteria to the cleaned dataset.
    
    Parameters:
        df: Cleaned pandas DataFrame
        gender: 'all', 'male', or 'female'
        age_group: 'all', '<40', '40-49', '50-59', '60-69', '70+'
        outcome: 'all', 'disease', or 'no_disease'
        cp: 'all', 'typical', 'atypical', 'non_anginal', 'asymptomatic'
    """
    filtered = df.copy()
    
    # Gender filter
    if gender and gender.lower() != "all":
        g = gender.lower()
        if g in ["male", "1"]:
            filtered = filtered[filtered["sex_label"] == "Male"]
        elif g in ["female", "0"]:
            filtered = filtered[filtered["sex_label"] == "Female"]
            
    # Age group filter
    if age_group and age_group.lower() != "all":
        ag = age_group.strip()
        filtered = filtered[filtered["age_group"] == ag]
        
    # Outcome filter
    if outcome and outcome.lower() != "all":
        out = outcome.lower().replace("-", "_").replace(" ", "_")
        if out in ["disease", "1"]:
            filtered = filtered[filtered["target_binary"] == 1]
        elif out in ["no_disease", "nodisease", "0"]:
            filtered = filtered[filtered["target_binary"] == 0]
            
    # Chest pain filter
    if cp and cp.lower() != "all":
        cp_val = cp.lower().replace("-", "_").replace(" ", "_")
        if "typical" in cp_val and "atypical" not in cp_val:
            filtered = filtered[filtered["cp_label"] == "Typical Angina"]
        elif "atypical" in cp_val:
            filtered = filtered[filtered["cp_label"] == "Atypical Angina"]
        elif "non_anginal" in cp_val or "nonanginal" in cp_val:
            filtered = filtered[filtered["cp_label"] == "Non-Anginal Pain"]
        elif "asymptomatic" in cp_val:
            filtered = filtered[filtered["cp_label"] == "Asymptomatic"]
            
    return filtered
