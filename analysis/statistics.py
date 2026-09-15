"""
Statistics and Visualization Computation Engine for Heart Disease Analytics.
Calculates summary KPIs, categorical distributions, clinical statistics, correlation matrices,
and SciPy-powered hypothesis tests.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats

CLINICAL_NUMERIC_VARS = [
    {"key": "age", "label": "Age", "unit": "years"},
    {"key": "trestbps", "label": "Resting Blood Pressure", "unit": "mm Hg"},
    {"key": "chol", "label": "Serum Cholesterol", "unit": "mg/dl"},
    {"key": "thalach", "label": "Max Heart Rate Achieved", "unit": "bpm"},
    {"key": "oldpeak", "label": "ST Depression (Exercise vs Rest)", "unit": "mm"}
]


def compute_summary_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate core overview KPIs dynamically from the dataset."""
    total = len(df)
    if total == 0:
        return {
            "total_patients": 0,
            "disease_cases": 0,
            "no_disease_cases": 0,
            "disease_prevalence": 0.0,
            "disease_prevalence_display": "N/A",
            "average_age": None,
            "average_age_display": "N/A",
            "average_cholesterol": None,
            "average_cholesterol_display": "N/A",
            "average_max_hr": None,
            "average_max_hr_display": "N/A",
            "average_resting_bp": None,
            "average_resting_bp_display": "N/A",
            "is_empty": True
        }
        
    disease_cases = int((df["target_binary"] == 1).sum())
    no_disease_cases = int((df["target_binary"] == 0).sum())
    disease_rate = (disease_cases / total) * 100
    
    avg_age = float(df["age"].mean()) if not df["age"].dropna().empty else None
    avg_chol = float(df["chol"].mean()) if not df["chol"].dropna().empty else None
    avg_max_hr = float(df["thalach"].mean()) if not df["thalach"].dropna().empty else None
    avg_bp = float(df["trestbps"].mean()) if not df["trestbps"].dropna().empty else None
    
    return {
        "total_patients": total,
        "disease_cases": disease_cases,
        "no_disease_cases": no_disease_cases,
        "disease_prevalence": round(disease_rate, 2),
        "disease_prevalence_display": f"{round(disease_rate, 1)}%",
        "average_age": round(avg_age, 2) if avg_age is not None else None,
        "average_age_display": f"{round(avg_age, 1)} yrs" if avg_age is not None else "N/A",
        "average_cholesterol": round(avg_chol, 2) if avg_chol is not None else None,
        "average_cholesterol_display": f"{round(avg_chol, 1)} mg/dl" if avg_chol is not None else "N/A",
        "average_max_hr": round(avg_max_hr, 2) if avg_max_hr is not None else None,
        "average_max_hr_display": f"{round(avg_max_hr, 1)} bpm" if avg_max_hr is not None else "N/A",
        "average_resting_bp": round(avg_bp, 2) if avg_bp is not None else None,
        "average_resting_bp_display": f"{round(avg_bp, 1)} mm Hg" if avg_bp is not None else "N/A",
        "is_empty": False
    }


def compute_disease_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute overall disease vs no-disease distribution for Doughnut chart."""
    if len(df) == 0:
        return {"labels": ["No Disease", "Disease"], "counts": [0, 0], "percentages": [0.0, 0.0]}
        
    no_disease = int((df["target_binary"] == 0).sum())
    disease = int((df["target_binary"] == 1).sum())
    total = len(df)
    
    return {
        "labels": ["No Disease", "Disease"],
        "counts": [no_disease, disease],
        "percentages": [
            round((no_disease / total) * 100, 1),
            round((disease / total) * 100, 1)
        ]
    }


def compute_age_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute age cohort distribution broken down by disease outcome."""
    categories = ["<40", "40-49", "50-59", "60-69", "70+"]
    disease_counts = []
    no_disease_counts = []
    disease_rates = []
    totals = []
    
    for cat in categories:
        sub = df[df["age_group"] == cat]
        t = len(sub)
        d = int((sub["target_binary"] == 1).sum())
        nd = int((sub["target_binary"] == 0).sum())
        rate = round((d / t) * 100, 1) if t > 0 else 0.0
        
        totals.append(t)
        disease_counts.append(d)
        no_disease_counts.append(nd)
        disease_rates.append(rate)
        
    return {
        "categories": categories,
        "disease_counts": disease_counts,
        "no_disease_counts": no_disease_counts,
        "totals": totals,
        "disease_rates": disease_rates
    }


def compute_gender_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute gender breakdown and outcome comparison."""
    categories = ["Male", "Female"]
    disease_counts = []
    no_disease_counts = []
    disease_rates = []
    totals = []
    
    for gender in categories:
        sub = df[df["sex_label"] == gender]
        t = len(sub)
        d = int((sub["target_binary"] == 1).sum())
        nd = int((sub["target_binary"] == 0).sum())
        rate = round((d / t) * 100, 1) if t > 0 else 0.0
        
        totals.append(t)
        disease_counts.append(d)
        no_disease_counts.append(nd)
        disease_rates.append(rate)
        
    return {
        "categories": categories,
        "disease_counts": disease_counts,
        "no_disease_counts": no_disease_counts,
        "totals": totals,
        "disease_rates": disease_rates
    }


def compute_chest_pain_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute chest pain types comparison with disease outcomes."""
    categories = ["Typical Angina", "Atypical Angina", "Non-Anginal Pain", "Asymptomatic"]
    disease_counts = []
    no_disease_counts = []
    disease_rates = []
    totals = []
    
    for cp in categories:
        sub = df[df["cp_label"] == cp]
        t = len(sub)
        d = int((sub["target_binary"] == 1).sum())
        nd = int((sub["target_binary"] == 0).sum())
        rate = round((d / t) * 100, 1) if t > 0 else 0.0
        
        totals.append(t)
        disease_counts.append(d)
        no_disease_counts.append(nd)
        disease_rates.append(rate)
        
    return {
        "categories": categories,
        "disease_counts": disease_counts,
        "no_disease_counts": no_disease_counts,
        "totals": totals,
        "disease_rates": disease_rates
    }


def _calc_stats(series: pd.Series) -> Dict[str, Any]:
    """Compute descriptive statistics: mean, median, IQR, std, min, max."""
    clean = series.dropna()
    if len(clean) == 0:
        return {
            "mean": None, "median": None, "iqr": None,
            "std": None, "min": None, "max": None, "count": 0
        }
    q75, q25 = np.percentile(clean, [75, 25])
    return {
        "mean": round(float(clean.mean()), 2),
        "median": round(float(clean.median()), 2),
        "iqr": round(float(q75 - q25), 2),
        "std": round(float(clean.std()), 2) if len(clean) > 1 else 0.0,
        "min": round(float(clean.min()), 2),
        "max": round(float(clean.max()), 2),
        "count": int(len(clean))
    }


def compute_clinical_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute comprehensive clinical factor descriptive analysis for numeric variables:
    Resting BP, Cholesterol, Max HR, ST Depression, and Age.
    Includes overall vs group comparisons (Disease vs No Disease).
    """
    results = {}
    
    disease_mask = df["target_binary"] == 1
    no_disease_mask = df["target_binary"] == 0
    
    for item in CLINICAL_NUMERIC_VARS:
        key = item["key"]
        label = item["label"]
        unit = item["unit"]
        
        series_all = df[key]
        series_dis = df.loc[disease_mask, key]
        series_nodis = df.loc[no_disease_mask, key]
        
        stat_all = _calc_stats(series_all)
        stat_dis = _calc_stats(series_dis)
        stat_nodis = _calc_stats(series_nodis)
        
        # Build 5-bin histogram data for visualization
        clean_vals = series_all.dropna()
        if len(clean_vals) >= 5 and clean_vals.min() < clean_vals.max():
            bins = np.linspace(clean_vals.min(), clean_vals.max(), 6)
            bin_labels = [f"{round(bins[i], 1)}-{round(bins[i+1], 1)}" for i in range(5)]
            
            dis_counts = []
            nodis_counts = []
            for i in range(5):
                lower = bins[i]
                upper = bins[i+1]
                if i == 4:
                    c_dis = int(((series_dis >= lower) & (series_dis <= upper)).sum())
                    c_nodis = int(((series_nodis >= lower) & (series_nodis <= upper)).sum())
                else:
                    c_dis = int(((series_dis >= lower) & (series_dis < upper)).sum())
                    c_nodis = int(((series_nodis >= lower) & (series_nodis < upper)).sum())
                dis_counts.append(c_dis)
                nodis_counts.append(c_nodis)
        else:
            bin_labels = []
            dis_counts = []
            nodis_counts = []
            
        # Data-driven descriptive note (strictly non-causal)
        if stat_dis["mean"] is not None and stat_nodis["mean"] is not None:
            diff = round(stat_dis["mean"] - stat_nodis["mean"], 2)
            direction = "higher" if diff > 0 else "lower"
            note = (
                f"In this dataset, the Disease cohort presents an average {label.lower()} "
                f"that is {abs(diff)} {unit} {direction} than the No Disease cohort "
                f"({stat_dis['mean']} vs {stat_nodis['mean']} {unit})."
            )
        else:
            note = "Insufficient data to compute group comparison."
            
        results[key] = {
            "label": label,
            "unit": unit,
            "overall": stat_all,
            "disease": stat_dis,
            "no_disease": stat_nodis,
            "note": note,
            "histogram": {
                "bins": bin_labels,
                "disease_counts": dis_counts,
                "no_disease_counts": nodis_counts
            }
        }
        
    return results


def compute_correlation_matrix(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute Pearson correlation matrix for numeric clinical variables.
    Returns structured data for the frontend correlation heatmap.
    """
    corr_cols = ["age", "trestbps", "chol", "thalach", "oldpeak", "target_binary"]
    labels_map = {
        "age": "Age",
        "trestbps": "Resting BP",
        "chol": "Cholesterol",
        "thalach": "Max Heart Rate",
        "oldpeak": "ST Depression",
        "target_binary": "Disease Status"
    }
    
    sub = df[corr_cols].dropna()
    if len(sub) < 3:
        return {"variables": [], "labels": [], "matrix": []}
        
    corr = sub.corr(method="pearson")
    matrix = []
    for row_col in corr_cols:
        row_vals = []
        for col_col in corr_cols:
            val = float(corr.loc[row_col, col_col])
            row_vals.append(round(val, 3) if not np.isnan(val) else 0.0)
        matrix.append(row_vals)
        
    return {
        "variables": corr_cols,
        "labels": [labels_map[c] for c in corr_cols],
        "matrix": matrix,
        "disclaimer": "Correlation indicates statistical association within this dataset and does not establish causation."
    }


def run_hypothesis_tests(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Run exploratory statistical tests via SciPy comparing Disease vs No Disease cohorts:
    - Numeric variables: Mann-Whitney U test & Independent two-sample t-test
    - Categorical variables: Chi-square test of independence
    
    All interpretations are non-causal and emphasize sample statistical associations.
    """
    tests = []
    alpha = 0.05
    
    disease = df[df["target_binary"] == 1]
    no_disease = df[df["target_binary"] == 0]
    
    # 1. Numeric Variables
    numeric_tests = [
        ("age", "Age"),
        ("thalach", "Max Heart Rate"),
        ("oldpeak", "ST Depression"),
        ("trestbps", "Resting Blood Pressure"),
        ("chol", "Serum Cholesterol")
    ]
    
    for var, label in numeric_tests:
        d_vals = disease[var].dropna()
        nd_vals = no_disease[var].dropna()
        
        if len(d_vals) > 2 and len(nd_vals) > 2:
            # Mann-Whitney U Test
            mwu_res = stats.mannwhitneyu(d_vals, nd_vals, alternative="two-sided")
            is_sig_mwu = bool(mwu_res.pvalue < alpha)
            p_val_mwu = float(mwu_res.pvalue)
            tests.append({
                "variable": label,
                "variable_type": "Numeric",
                "test": "Mann-Whitney U Test",
                "statistic": round(float(mwu_res.statistic), 2),
                "p_value": float(f"{p_val_mwu:.4e}" if p_val_mwu < 0.0001 else f"{p_val_mwu:.4f}"),
                "p_value_display": "< 0.0001" if p_val_mwu < 0.0001 else f"{p_val_mwu:.4f}",
                "significance": "Statistically Significant" if is_sig_mwu else "Not Significant",
                "is_significant": is_sig_mwu,
                "interpretation": (
                    f"Evidence of a statistically significant rank difference in {label.lower()} between "
                    f"disease and no-disease cohorts in this sample (p = {p_val_mwu:.4f} < 0.05)."
                    if is_sig_mwu else
                    f"No statistically significant difference in {label.lower()} rank distributions detected "
                    f"at alpha=0.05 (p = {p_val_mwu:.4f} >= 0.05)."
                )
            })
            
            # Independent two-sample t-test
            ttest_res = stats.ttest_ind(d_vals, nd_vals, equal_var=False)
            is_sig_t = bool(ttest_res.pvalue < alpha)
            p_val_t = float(ttest_res.pvalue)
            tests.append({
                "variable": label,
                "variable_type": "Numeric",
                "test": "Two-Sample Welch's t-test",
                "statistic": round(float(ttest_res.statistic), 2),
                "p_value": float(f"{p_val_t:.4e}" if p_val_t < 0.0001 else f"{p_val_t:.4f}"),
                "p_value_display": "< 0.0001" if p_val_t < 0.0001 else f"{p_val_t:.4f}",
                "significance": "Statistically Significant" if is_sig_t else "Not Significant",
                "is_significant": is_sig_t,
                "interpretation": (
                    f"Mean {label.lower()} differs significantly between cohorts in this sample (p < 0.05)."
                    if is_sig_t else
                    f"Mean {label.lower()} difference between cohorts is not statistically significant at alpha=0.05."
                )
            })
            
    # 2. Categorical Variables (Chi-Square Test of Independence)
    categorical_tests = [
        ("sex_label", "Biological Sex"),
        ("cp_label", "Chest Pain Type"),
        ("exang_label", "Exercise-Induced Angina"),
        ("fbs_label", "Fasting Blood Sugar")
    ]
    
    for var, label in categorical_tests:
        valid_sub = df[[var, "target_binary"]].dropna()
        if len(valid_sub) > 5:
            contingency_table = pd.crosstab(valid_sub[var], valid_sub["target_binary"])
            if contingency_table.shape[0] > 1 and contingency_table.shape[1] > 1:
                chi2_stat, p_val, dof, _ = stats.chi2_contingency(contingency_table)
                is_sig = bool(p_val < alpha)
                p_val_f = float(p_val)
                tests.append({
                    "variable": label,
                    "variable_type": "Categorical",
                    "test": f"Chi-Square Test (df={dof})",
                    "statistic": round(float(chi2_stat), 2),
                    "p_value": float(f"{p_val_f:.4e}" if p_val_f < 0.0001 else f"{p_val_f:.4f}"),
                    "p_value_display": "< 0.0001" if p_val_f < 0.0001 else f"{p_val_f:.4f}",
                    "significance": "Statistically Significant" if is_sig else "Not Significant",
                    "is_significant": is_sig,
                    "interpretation": (
                        f"There is evidence of a statistically significant association between {label.lower()} "
                        f"and heart disease outcome in this dataset (p < 0.05)."
                        if is_sig else
                        f"No statistically significant association observed between {label.lower()} "
                        f"and outcome at alpha=0.05."
                    )
                })
                
    return tests
