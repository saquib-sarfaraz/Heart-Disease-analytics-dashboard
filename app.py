"""
Flask Application Backend for Heart Disease Analytics Dashboard.
Exposes REST APIs for dynamic KPI calculations, statistical distributions,
hypothesis testing, correlation analysis, dynamic narrative insights, and patient data exploration.
"""

import os
import math
from typing import Tuple, Dict, Any
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np

from analysis.cleaning import load_and_clean_data, filter_dataframe
from analysis.statistics import (
    compute_summary_kpis,
    compute_disease_distribution,
    compute_age_analysis,
    compute_gender_analysis,
    compute_chest_pain_analysis,
    compute_clinical_analysis,
    compute_correlation_matrix,
    run_hypothesis_tests
)
from analysis.insights import generate_dynamic_insights

app = Flask(__name__)

# Global cached dataset loaded on startup
try:
    RAW_DF = load_and_clean_data()
    DATA_LOAD_ERROR = None
except Exception as e:
    RAW_DF = None
    DATA_LOAD_ERROR = str(e)


def get_filtered_df_from_request() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Extract filter parameters from request query and apply to cleaned dataset."""
    if RAW_DF is None:
        raise RuntimeError(DATA_LOAD_ERROR or "Dataset failed to load on server.")
        
    gender = request.args.get("gender", "all").strip()
    age_group = request.args.get("age_group", "all").strip()
    outcome = request.args.get("outcome", "all").strip()
    cp = request.args.get("cp", "all").strip()
    
    filtered_df = filter_dataframe(
        RAW_DF,
        gender=gender,
        age_group=age_group,
        outcome=outcome,
        cp=cp
    )
    
    filters_applied = {
        "gender": gender,
        "age_group": age_group,
        "outcome": outcome,
        "cp": cp
    }
    
    return filtered_df, filters_applied


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found", "status": 404}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error occurred", "status": 500}), 500


@app.route("/")
def index():
    """Render the single-page analytics dashboard frontend."""
    return render_template("index.html")


@app.route("/api/summary", methods=["GET"])
def api_summary():
    """Endpoint for KPI summary cards."""
    try:
        df, filters = get_filtered_df_from_request()
        kpis = compute_summary_kpis(df)
        return jsonify({
            "success": True,
            "data": kpis,
            "filters": filters
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/distribution", methods=["GET"])
def api_distribution():
    """Endpoint for disease status distribution (doughnut chart)."""
    try:
        df, filters = get_filtered_df_from_request()
        dist = compute_disease_distribution(df)
        return jsonify({
            "success": True,
            "data": dist,
            "filters": filters
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/age-analysis", methods=["GET"])
def api_age_analysis():
    """Endpoint for age cohort distribution by disease status."""
    try:
        df, filters = get_filtered_df_from_request()
        data = compute_age_analysis(df)
        return jsonify({
            "success": True,
            "data": data,
            "filters": filters
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/gender-analysis", methods=["GET"])
def api_gender_analysis():
    """Endpoint for gender comparison by disease status."""
    try:
        df, filters = get_filtered_df_from_request()
        data = compute_gender_analysis(df)
        return jsonify({
            "success": True,
            "data": data,
            "filters": filters
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/chest-pain-analysis", methods=["GET"])
def api_chest_pain_analysis():
    """Endpoint for chest pain types vs disease status."""
    try:
        df, filters = get_filtered_df_from_request()
        data = compute_chest_pain_analysis(df)
        return jsonify({
            "success": True,
            "data": data,
            "filters": filters
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/clinical-analysis", methods=["GET"])
def api_clinical_analysis():
    """Endpoint for clinical factor statistics and comparison histograms."""
    try:
        df, filters = get_filtered_df_from_request()
        data = compute_clinical_analysis(df)
        return jsonify({
            "success": True,
            "data": data,
            "filters": filters
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/correlation", methods=["GET"])
def api_correlation():
    """Endpoint for Pearson correlation matrix of numeric clinical parameters."""
    try:
        df, filters = get_filtered_df_from_request()
        data = compute_correlation_matrix(df)
        return jsonify({
            "success": True,
            "data": data,
            "filters": filters
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/statistics", methods=["GET"])
def api_statistics():
    """Endpoint for SciPy hypothesis tests and descriptive comparisons."""
    try:
        df, filters = get_filtered_df_from_request()
        tests = run_hypothesis_tests(df)
        return jsonify({
            "success": True,
            "data": {
                "tests": tests,
                "alpha": 0.05,
                "note": "Hypothesis tests evaluate sample statistical associations and do not imply clinical causality."
            },
            "filters": filters
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/insights", methods=["GET"])
def api_insights():
    """Endpoint for dynamic analytical findings generated from data."""
    try:
        df, filters = get_filtered_df_from_request()
        insights = generate_dynamic_insights(df)
        return jsonify({
            "success": True,
            "data": insights,
            "filters": filters
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/patients", methods=["GET"])
def api_patients():
    """
    Searchable, sortable, and paginated patient data table explorer endpoint.
    Excludes server filesystem references and ensures clean JSON serializability.
    """
    try:
        df, filters = get_filtered_df_from_request()
        
        # Search query
        search_query = request.args.get("search", "").strip().lower()
        if search_query:
            mask = (
                df["patient_id"].astype(str).str.contains(search_query, case=False, na=False) |
                df["age"].astype(str).str.contains(search_query, case=False, na=False) |
                df["sex_label"].str.lower().str.contains(search_query, case=False, na=False) |
                df["cp_label"].str.lower().str.contains(search_query, case=False, na=False) |
                df["trestbps"].astype(str).str.contains(search_query, case=False, na=False) |
                df["chol"].astype(str).str.contains(search_query, case=False, na=False) |
                df["thalach"].astype(str).str.contains(search_query, case=False, na=False) |
                df["oldpeak"].astype(str).str.contains(search_query, case=False, na=False) |
                df["outcome_label"].str.lower().str.contains(search_query, case=False, na=False)
            )
            df = df[mask]
            
        # Sorting
        sort_col = request.args.get("sort", "patient_id").strip()
        order = request.args.get("order", "asc").strip().lower()
        ascending = order != "desc"
        
        valid_cols = [
            "patient_id", "age", "sex_label", "cp_label", 
            "trestbps", "chol", "thalach", "oldpeak", "outcome_label"
        ]
        
        if sort_col in valid_cols:
            df = df.sort_values(by=sort_col, ascending=ascending)
            
        total_records = len(df)
        
        # Pagination
        try:
            page = max(1, int(request.args.get("page", 1)))
        except ValueError:
            page = 1
            
        try:
            per_page = max(5, min(100, int(request.args.get("per_page", 10))))
        except ValueError:
            per_page = 10
            
        total_pages = max(1, math.ceil(total_records / per_page))
        if page > total_pages and total_records > 0:
            page = total_pages
            
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_df = df.iloc[start_idx:end_idx]
        
        # Prepare structured records for frontend table
        records = []
        for _, row in page_df.iterrows():
            records.append({
                "patient_id": int(row["patient_id"]),
                "age": int(row["age"]) if not pd.isna(row["age"]) else None,
                "sex": str(row["sex_label"]),
                "chest_pain": str(row["cp_label"]),
                "resting_bp": int(row["trestbps"]) if not pd.isna(row["trestbps"]) else None,
                "cholesterol": int(row["chol"]) if not pd.isna(row["chol"]) else None,
                "max_hr": int(row["thalach"]) if not pd.isna(row["thalach"]) else None,
                "oldpeak": round(float(row["oldpeak"]), 1) if not pd.isna(row["oldpeak"]) else None,
                "outcome": str(row["outcome_label"]),
                "target_binary": int(row["target_binary"])
            })
            
        return jsonify({
            "success": True,
            "data": records,
            "page": page,
            "per_page": per_page,
            "total": total_records,
            "pages": total_pages,
            "filters": filters
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Heart Disease Analytics Dashboard server on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
