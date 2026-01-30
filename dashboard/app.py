# app.py
import sys
import os

# Allow imports from src/ directory
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import streamlit as st
import pandas as pd

# Import UI components
from ui_components import (
    load_ui_css,
    render_bias_card,
    render_explanation,
    render_traffic_light_legend,
    render_representation_table,
    render_metric_cards
)

# Import data loading & bias logic
from src.data_loader import load_dataset, analyze_columns
from src.bias_metrics import (
    representation_and_sampling_bias,
    label_bias,
    historical_bias,
    statistical_parity_difference,
    disparate_impact,
    final_bias_verdict,
    unsupervised_bias_verdict
)

# =================================================
# PAGE CONFIGURATION
# =================================================
st.set_page_config(
    page_title="unbiasED - Bias Detection Dashboard",
    layout="wide",
    page_icon="🔍",
    initial_sidebar_state="collapsed"
)

# Load CSS FIRST - this is critical for theme to work
load_ui_css()

# =================================================
# HELPER FUNCTIONS
# =================================================
def get_eligible_target_columns(df, sensitive_attr):
    """Returns columns suitable to act as outcome variables"""
    eligible = []

    for col in df.columns:
        # Exclude sensitive attribute
        if col == sensitive_attr:
            continue

        # Exclude identifier-like columns
        if df[col].nunique() / len(df) > 0.7:
            continue

        unique_vals = df[col].dropna().unique()

        # Must have at least 2 classes
        if len(unique_vals) < 2:
            continue

        # Exclude demographic-like categorical columns but NEVER exclude binary outcomes
        if df[col].dtype == "object" and len(unique_vals) > 2 and len(unique_vals) <= 10:
            continue

        eligible.append(col)

    return eligible

def detect_bias_types(min_rep, label_diff, hist_diff, max_spd, max_di_dev):
    """Detect types of bias present"""
    bias_types = []

    if min_rep < 0.4:
        bias_types.append("Representation Bias")

    if label_diff > 0.2:
        bias_types.append("Label Bias")

    if hist_diff > 0.2:
        bias_types.append("Historical Bias")

    if max_spd > 0.1 or max_di_dev > 0.2:
        bias_types.append("Outcome Bias")

    if not bias_types:
        bias_types.append("No Significant Bias Detected")

    return bias_types

# =================================================
# MAIN APPLICATION
# =================================================


# Main header with full width
st.markdown("""
<div style="width: 100%; background: linear-gradient(135deg, #87CEEB, #4682B4); 
            padding: 2rem; border-radius: 10px; margin-bottom: 2rem; text-align: center;">
    <h1 style="color: white; margin: 0;">unbiasED - Bias Detection Dashboard</h1>
    <p style="color: white; opacity: 0.9; margin: 10px 0 0 0;">
        Upload a CSV or Excel file to analyze bias in your dataset
    </p>
</div>
""", unsafe_allow_html=True)

# File upload section with full width
st.markdown("### 📁 Upload Your Dataset")
uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xls", "xlsx"],
    label_visibility="collapsed",
    help="Maximum file size: 200MB"
)

if uploaded_file is None:
    # Welcome section with info cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background-color: var(--card-bg); padding: 1.5rem; border-radius: 10px; 
                    border-left: 5px solid #87CEEB; height: 100%;">
            <h3>📊 How It Works</h3>
            <p>1. Upload your dataset</p>
            <p>2. Select analysis type</p>
            <p>3. Choose sensitive attribute</p>
            <p>4. Get bias analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: var(--card-bg); padding: 1.5rem; border-radius: 10px; 
                    border-left: 5px solid #4682B4; height: 100%;">
            <h3>🎯 What We Analyze</h3>
            <p>• Representation Bias</p>
            <p>• Label Bias</p>
            <p>• Historical Bias</p>
            <p>• Outcome Bias</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background-color: var(--card-bg); padding: 1.5rem; border-radius: 10px; 
                    border-left: 5px solid #5D8AA8; height: 100%;">
            <h3>⚙️ Supported Formats</h3>
            <p>• CSV (.csv)</p>
            <p>• Excel (.xls, .xlsx)</p>
            <p>• Up to 200MB</p>
            <p>• Structured data</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("👆 Please upload a dataset to begin analysis")
    st.stop()

# Load data
try:
    with st.spinner("Loading dataset..."):
        df = load_dataset(uploaded_file)
    
    st.success(f"✅ Dataset loaded successfully! **{df.shape[0]} rows × {df.shape[1]} columns**")
    
    # Dataset preview in tabs
    tab1, tab2 = st.tabs(["📋 Data Preview", "📊 Dataset Info"])
    
    with tab1:
        st.dataframe(df.head(), use_container_width=True)
    
    with tab2:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Rows", df.shape[0])
        with col2:
            st.metric("Columns", df.shape[1])
        with col3:
            st.metric("Missing Values", df.isnull().sum().sum())
        with col4:
            st.metric("Data Types", len(df.dtypes.unique()))
        
except Exception as e:
    st.error(f"❌ Error reading file: {str(e)}")
    st.stop()

# Configuration section - full width
st.markdown("---")
st.markdown("### ⚙️ Analysis Configuration")

# Create two columns for configuration
config_col1, config_col2 = st.columns(2)

with config_col1:
    dataset_type = st.radio(
        "**Dataset Type**",
        ["Supervised (has target/labels)", "Unsupervised (no labels)"],
        horizontal=True
    )

is_supervised = dataset_type.startswith("Supervised")

with config_col2:
    if is_supervised:
        st.info("🔍 **Supervised Mode** - Will analyze outcome fairness")
    else:
        st.warning("⚠️ **Unsupervised Mode** - Only representation analysis")

# Sensitive attribute selection
st.markdown("### 🎯 Select Sensitive Attribute")
st.write("Choose the demographic feature to analyze for bias (e.g., gender, race, age group).")

eligible_sensitive, excluded_columns = analyze_columns(df)

if not eligible_sensitive:
    st.error("No suitable sensitive attributes found in your dataset.")
    st.stop()

sel_col, info_col = st.columns([3, 1])

with sel_col:
    sensitive_attr = st.selectbox(
        "Select sensitive attribute:",
        options=["-- Select --"] + eligible_sensitive,
        label_visibility="collapsed"
    )

with info_col:
    if sensitive_attr != "-- Select --":
        unique_vals = df[sensitive_attr].dropna().unique()
        st.metric("Unique Groups", len(unique_vals))

if sensitive_attr == "-- Select --":
    st.info("Please select a sensitive attribute to proceed")
    st.stop()

# =================================================
# SUPERVISED PATH
# =================================================
if is_supervised:
    st.markdown("### 🎯 Select Target Variable")
    
    eligible_targets = get_eligible_target_columns(df, sensitive_attr)

    if not eligible_targets:
        st.warning("No valid outcome variable found. Supervised bias analysis cannot be performed.")
        st.stop()

    target_col, target_info = st.columns([3, 1])
    
    with target_col:
        target_attr = st.selectbox(
            "Select outcome variable:",
            options=["-- Select --"] + eligible_targets,
            label_visibility="collapsed"
        )

    with target_info:
        if target_attr != "-- Select --":
            target_values = df[target_attr].dropna().unique()
            st.metric("Unique Outcomes", len(target_values))

    positive_label = None

    if target_attr != "-- Select --":
        st.markdown("### 📊 Define Positive Outcome")
        target_values = df[target_attr].dropna().unique()

        if len(target_values) == 2:
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Available outcomes:**")
                for val in target_values:
                    st.write(f"• {val}")
            with col2:
                positive_label = st.selectbox(
                    "Select POSITIVE outcome:",
                    options=target_values,
                    label_visibility="collapsed"
                )
        else:
            st.info("Multi-class outcome detected. Using one-vs-rest binarization.")
            positive_label = st.selectbox(
                "Select the POSITIVE class for analysis:",
                options=target_values
            )

    # Validation
    if target_attr == "-- Select --" or positive_label is None:
        st.info("Please complete all selections to proceed.")
        st.stop()

    elif sensitive_attr == target_attr:
        st.warning("Sensitive attribute and target variable must be different.")
        st.stop()

    # Run analysis button
    st.markdown("---")
    if st.button("🚀 **Run Comprehensive Bias Analysis**", 
                 type="primary", 
                 use_container_width=True,
                 icon="🚀"):
        
        with st.spinner("Analyzing bias patterns..."):
            # Calculate metrics
            rep_df, min_rep = representation_and_sampling_bias(df, sensitive_attr)
            label_diff = label_bias(df, sensitive_attr, target_attr, positive_label)
            hist_diff = historical_bias(df, sensitive_attr, target_attr, positive_label)
            
            reference_group = rep_df.loc[rep_df["count"].idxmax(), "group"]
            
            max_spd = statistical_parity_difference(
                df, sensitive_attr, target_attr, positive_label, reference_group
            )
            max_di_dev = disparate_impact(
                df, sensitive_attr, target_attr, positive_label, reference_group
            )
            
            result = final_bias_verdict(
                min_representation=min_rep,
                label_diff=label_diff,
                historical_diff=hist_diff,
                max_spd=max_spd,
                max_di_deviation=max_di_dev
            )
            bias_types = detect_bias_types(
                min_rep,
                label_diff,
                hist_diff,
                max_spd,
                max_di_dev
            )
        
        # =================================================
        # DISPLAY RESULTS - FULL WIDTH LAYOUT
        # =================================================
        st.markdown("---")
        st.markdown("## 📊 **Analysis Results**")
        
        # Top row: Main verdict and traffic lights
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Final verdict - main focus
            st.markdown("### 🎯 Final Verdict")
            render_bias_card(result)
            
            # Quick metrics in a row
            st.markdown("### 📈 Key Metrics")
            metric_cols = st.columns(5)
            metrics = [
                ("Min Representation", min_rep, "#87CEEB"),
                ("Label Bias", label_diff, "#FFC107"),
                ("Historical Bias", hist_diff, "#FF9800"),
                ("Statistical Parity", max_spd, "#4CAF50"),
                ("Disparate Impact", max_di_dev, "#F44336")
            ]
            
            for idx, (name, value, color) in enumerate(metrics):
                with metric_cols[idx]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; background-color: {color}20; 
                                border-radius: 8px; border: 1px solid {color}40;">
                        <div style="font-size: 0.9rem; color: #666;">{name}</div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: {color};">{value:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Group representation table
            st.markdown("### 👥 Group Representation")
            rep_display = rep_df.copy()
            rep_display['proportion'] = rep_display['proportion'].apply(lambda x: f"{x:.1%}")
            st.dataframe(rep_display, use_container_width=True)
        
        with col2:
            # Traffic lights on the right
            st.markdown("### 🚦 Bias Severity Guide")
            
            bias_level = result["bias_percentage"]
            
            # Current bias indicator
            if bias_level < 30:
                current_color = "#4CAF50"
                current_text = "Low Bias"
                icon = "✅"
            elif bias_level < 60:
                current_color = "#FFC107"
                current_text = "Moderate Bias"
                icon = "⚠️"
            else:
                current_color = "#F44336"
                current_text = "High Bias"
                icon = "🚨"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background-color: {current_color}20; 
                        border-radius: 10px; border: 2px solid {current_color}; margin-bottom: 20px;">
                <div style="font-size: 3rem; margin: 10px 0;">{icon}</div>
                <h2 style="color: {current_color}; margin: 10px 0;">{bias_level}%</h2>
                <h3 style="color: {current_color}; margin: 0;">{current_text}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Traffic light guide
            st.markdown("""
            <div style="background-color: var(--card-bg); padding: 20px; border-radius: 10px; 
                        border: 1px solid var(--border-color);">
                <div style="display: flex; align-items: center; margin-bottom: 15px; padding: 10px; 
                            background-color: #4CAF5020; border-radius: 8px;">
                    <div style="width: 20px; height: 20px; background-color: #4CAF50; 
                                border-radius: 50%; margin-right: 15px;"></div>
                    <div>
                        <strong style="color: #4CAF50;">Low Bias</strong><br>
                        <small>&lt; 30% - Minimal risk</small>
                    </div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 15px; padding: 10px; 
                            background-color: #FFC10720; border-radius: 8px;">
                    <div style="width: 20px; height: 20px; background-color: #FFC107; 
                                border-radius: 50%; margin-right: 15px;"></div>
                    <div>
                        <strong style="color: #FFC107;">Moderate Bias</strong><br>
                        <small>30-60% - Monitor closely</small>
                    </div>
                </div>
                <div style="display: flex; align-items: center; padding: 10px; 
                            background-color: #F4433620; border-radius: 8px;">
                    <div style="width: 20px; height: 20px; background-color: #F44336; 
                                border-radius: 50%; margin-right: 15px;"></div>
                    <div>
                        <strong style="color: #F44336;">High Bias</strong><br>
                        <small>&gt; 60% - Requires action</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Quick actions
            st.markdown("### ⚡ Quick Actions")
            if "Representation Bias" in bias_types:
                st.error("**Improve Representation**\n\nCollect more data for underrepresented groups")
            if "Outcome Bias" in bias_types:
                st.error("**Adjust Outcomes**\n\nUse fairness-aware algorithms")
        
        # Bottom section: Bias types and recommendations
        st.markdown("---")
        
        # Bias types in cards
        st.markdown("### 🔍 Identified Bias Types")
        bias_cols = st.columns(len(bias_types))
        
        for idx, bias in enumerate(bias_types):
            with bias_cols[idx]:
                if "No Significant" in bias:
                    bg_color = "#4CAF5020"
                    border_color = "#4CAF50"
                    emoji = "✅"
                else:
                    bg_color = "#FFC10720"
                    border_color = "#FFC107"
                    emoji = "⚠️"
                
                st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; 
                            border-left: 5px solid {border_color}; text-align: center; height: 100%;">
                    <div style="font-size: 2rem;">{emoji}</div>
                    <strong>{bias}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        # Recommendations in expandable sections
        st.markdown("### 🛠️ Recommendations")
        
        for bias in bias_types:
            if "No Significant" in bias:
                continue
                
            with st.expander(f"💡 Fix {bias}", expanded=False):
                if bias == "Representation Bias":
                    st.markdown("""
**What went wrong?**  
Some groups appear much less frequently in the dataset than others.

**Why is this a problem?**  
The model learns mostly from dominant groups and performs poorly for underrepresented ones.

**What you can do next:**  
- Collect more real data for missing or small groups  
- Ensure balanced data collection across groups  
- Use re-weighting during model training (instead of duplicating data)
""")

                elif bias == "Label Bias":
                    st.markdown("""
**What went wrong?**  
The labels (decisions or outcomes) may be influenced by human judgment or systemic bias.

**Why is this a problem?**  
The model treats biased labels as correct and learns unfair patterns.

**What you can do next:**  
- Audit how labels were assigned  
- Use multiple annotators instead of a single decision-maker  
- Reduce the influence of biased labels during training
""")

                elif bias == "Historical Bias":
                    st.markdown("""
**What went wrong?**  
The dataset reflects unfair decisions made in the past.

**Why is this a problem?**  
Even a perfect model will reproduce past discrimination.

**What you can do next:**  
- Add fairness constraints during model training  
- Apply fairness correction after predictions  
- Question whether historical data still represents today’s reality
""")

                elif bias == "Outcome Bias":
                    st.markdown("""
**What went wrong?**  
Different groups receive different outcomes even when they have similar data.

**Why is this a problem?**  
This can cause unfair approvals, rejections, or predictions in real-world use.

**What you can do next:**  
- Use fairness-aware algorithms (e.g., Fairlearn, AIF360)  
- Adjust decision thresholds separately for each group  
- Review model outputs before deployment
""")


# =================================================
# UNSUPERVISED PATH
# =================================================
else:
    st.markdown("---")
    
    if st.button("🚀 **Analyze Representation Bias**", 
                 type="primary", 
                 use_container_width=True,
                 icon="📊"):
        
        with st.spinner("Analyzing group representation..."):
            rep_df, min_rep = representation_and_sampling_bias(df, sensitive_attr)
            result = unsupervised_bias_verdict(min_rep)
        
        # Display results
        st.markdown("---")
        st.markdown("## 📊 **Unsupervised Analysis Results**")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            render_bias_card(result)
            
            st.markdown("### 👥 Group Representation")
            rep_display = rep_df.copy()
            rep_display['proportion'] = rep_display['proportion'].apply(lambda x: f"{x:.1%}")
            st.dataframe(rep_display, use_container_width=True)
            
            st.info("""
            **Note:** This is unsupervised analysis. 
            Without outcome labels, we can only analyze representation bias.
            Consider adding labels for comprehensive fairness assessment.
            """)
        
        with col2:
            # Representation guide
            st.markdown("### 🎯 Representation Guide")
            
            if min_rep >= 0.4:
                color = "#4CAF50"
                level = "Good"
                emoji = "✅"
            elif min_rep >= 0.3:
                color = "#FFC107"
                level = "Moderate"
                emoji = "⚠️"
            else:
                color = "#F44336"
                level = "High Risk"
                emoji = "🚨"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 25px; background-color: {color}20; 
                        border-radius: 10px; border: 2px solid {color}; margin-bottom: 20px;">
                <div style="font-size: 3rem; margin: 10px 0;">{emoji}</div>
                <h1 style="color: {color}; margin: 10px 0; font-size: 2.5rem;">{min_rep:.1%}</h1>
                <h3 style="color: {color}; margin: 0;">{level}</h3>
                <small>Minimum group representation</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Guide
            st.markdown("""
            <div style="background-color: var(--card-bg); padding: 20px; border-radius: 10px; 
                        border: 1px solid var(--border-color);">
                <div style="margin-bottom: 10px;">
                    <strong>≥ 40%</strong> → Balanced representation
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>30-40%</strong> → Moderate risk
                </div>
                <div>
                    <strong>&lt; 30%</strong> → High risk of bias
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recommendations
            st.markdown("### 💡 Recommendations")
            if min_rep < 0.4:
                st.error("**Improve representation:**\n\nCollect more data for underrepresented groups")
            else:
                st.success("**Good representation:**\n\nContinue monitoring as you add more data")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-color); opacity: 0.7; padding: 15px;">
    <p>🔍 <strong>Bias Detection Dashboard</strong> | Made with Streamlit</p>
    <p style="font-size: 0.9rem;">
</div>
""", unsafe_allow_html=True)