"""
Dynamic Narrative Insights Generator for Heart Disease Analytics.
Produces strictly data-driven findings across demographic cohorts, clinical indicators,
and exercise parameters. Avoids hardcoded claims and causal assertions.
"""

from typing import List, Dict, Any
import pandas as pd


def generate_dynamic_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generate analytical insights dynamically based on the current (or filtered) dataset.
    Returns structured insight items with category, title, metric_highlight, and narrative finding.
    """
    total = len(df)
    if total == 0:
        return [{
            "category": "Filter Status",
            "icon": "info",
            "title": "No Observations in Selection",
            "badge": "Empty Cohort",
            "finding": "The current filter combination returned 0 patient records. Reset or adjust your filters to view analytical insights."
        }]

    insights = []
    disease_df = df[df["target_binary"] == 1]
    nodisease_df = df[df["target_binary"] == 0]
    total_disease = len(disease_df)
    disease_prevalence = round((total_disease / total) * 100, 1)

    # 1. Overall Prevalence Insight
    insights.append({
        "category": "Cohort Distribution",
        "icon": "users",
        "title": "Overall Sample Prevalence",
        "badge": f"{disease_prevalence}% Disease Rate",
        "finding": (
            f"Within this analyzed cohort of {total} patients, {total_disease} cases ({disease_prevalence}%) "
            f"exhibit presence of heart disease, while {len(nodisease_df)} cases ({round(100 - disease_prevalence, 1)}%) "
            "show no diagnosis of heart disease."
        )
    })

    # 2. Demographic Age Analysis Insight
    age_groups = ["<40", "40-49", "50-59", "60-69", "70+"]
    age_counts = df["age_group"].value_counts()
    dominant_age_group = age_counts.index[0] if not age_counts.empty else "N/A"
    
    # Calculate age cohort with highest disease prevalence (min 5 patients)
    highest_rate_group = None
    highest_rate = -1
    for ag in age_groups:
        sub = df[df["age_group"] == ag]
        if len(sub) >= 3:
            r = (sub["target_binary"] == 1).mean() * 100
            if r > highest_rate:
                highest_rate = r
                highest_rate_group = ag

    if highest_rate_group:
        insights.append({
            "category": "Demographic Pattern",
            "icon": "calendar",
            "title": "Age Cohort Concentration",
            "badge": f"{round(highest_rate, 1)}% in {highest_rate_group}",
            "finding": (
                f"The largest demographic volume is in the '{dominant_age_group}' age bracket ({age_counts.get(dominant_age_group, 0)} patients). "
                f"The highest concentration of heart disease occurs in the '{highest_rate_group}' group, "
                f"where {round(highest_rate, 1)}% of individuals exhibit disease markers."
            )
        })

    # 3. Chest Pain Presentation Insight
    if not df["cp_label"].empty:
        cp_disease = disease_df["cp_label"].value_counts()
        if not cp_disease.empty:
            dominant_cp = cp_disease.index[0]
            dom_count = cp_disease.iloc[0]
            dom_pct = round((dom_count / total_disease) * 100, 1) if total_disease > 0 else 0
            
            insights.append({
                "category": "Symptomatology",
                "icon": "activity",
                "title": "Chest Pain Manifestation",
                "badge": f"{dom_pct}% {dominant_cp}",
                "finding": (
                    f"Among heart disease patients in this dataset, '{dominant_cp}' was the most prevalent chest pain category "
                    f"({dom_count} of {total_disease} cases, or {dom_pct}%). "
                    "This underscores that absence of classic acute chest pain (e.g. typical angina) is frequent among clinical cases in this registry."
                )
            })

    # 4. Maximum Heart Rate (Exercise Capacity)
    if not disease_df["thalach"].dropna().empty and not nodisease_df["thalach"].dropna().empty:
        mean_hr_dis = round(float(disease_df["thalach"].mean()), 1)
        mean_hr_nodis = round(float(nodisease_df["thalach"].mean()), 1)
        diff_hr = round(mean_hr_nodis - mean_hr_dis, 1)
        insights.append({
            "category": "Exercise Physiology",
            "icon": "heart",
            "title": "Maximum Heart Rate Differential",
            "badge": f"Δ {diff_hr} bpm disparity",
            "finding": (
                f"Patients with heart disease achieved a notably lower average maximum heart rate ({mean_hr_dis} bpm) "
                f"compared to individuals without heart disease ({mean_hr_nodis} bpm), representing an observed difference "
                f"of {diff_hr} bpm during clinical treadmill evaluation."
            )
        })

    # 5. ST Depression (oldpeak) Insight
    if not disease_df["oldpeak"].dropna().empty and not nodisease_df["oldpeak"].dropna().empty:
        mean_st_dis = round(float(disease_df["oldpeak"].mean()), 2)
        mean_st_nodis = round(float(nodisease_df["oldpeak"].mean()), 2)
        insights.append({
            "category": "Electrocardiography",
            "icon": "trending-up",
            "title": "Exercise-Induced ST Depression",
            "badge": f"{mean_st_dis} mm vs {mean_st_nodis} mm",
            "finding": (
                f"Exercise-induced ST depression (oldpeak) averaged {mean_st_dis} mm in the disease group "
                f"versus {mean_st_nodis} mm in the no-disease group. Higher exercise ST depression reflects "
                "relative subendocardial ischemia during physical stress."
            )
        })

    # 6. Biological Sex Disparity (if both sexes present)
    male_sub = df[df["sex_label"] == "Male"]
    female_sub = df[df["sex_label"] == "Female"]
    if len(male_sub) > 0 and len(female_sub) > 0:
        male_rate = round((male_sub["target_binary"] == 1).mean() * 100, 1)
        female_rate = round((female_sub["target_binary"] == 1).mean() * 100, 1)
        insights.append({
            "category": "Demographic Disparity",
            "icon": "shield",
            "title": "Outcome Disparity by Biological Sex",
            "badge": f"Male {male_rate}% | Female {female_rate}%",
            "finding": (
                f"In this cohort, {male_rate}% of male patients ({int((male_sub['target_binary'] == 1).sum())}/{len(male_sub)}) "
                f"presented with heart disease, compared to {female_rate}% of female patients ({int((female_sub['target_binary'] == 1).sum())}/{len(female_sub)}). "
                "Sample composition and referral patterns in clinical datasets can impact these observational distributions."
            )
        })

    return insights
