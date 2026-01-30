# ui_components.py
import streamlit as st

def load_ui_css():
    """Load custom CSS for the application"""
    st.markdown("""
    <style>
    /* Base styles */
    .main {
        padding: 0;
    }
    
    .stApp {
        max-width: 100%;
        padding: 0;
    }
    
    /* Card styling */
    .custom-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #87CEEB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .custom-card {
            padding: 1rem;
        }
    }
    
    /* Streamlit element overrides */
    .stButton > button {
        background: linear-gradient(135deg, #87CEEB, #4682B4);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

def create_theme_toggle():
    """Create theme toggle button"""
    # Initialize theme in session state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Create toggle button
    col1, col2, col3 = st.columns([5, 5, 1])
    with col3:
        if st.button("🌓", key="theme_toggle", help="Toggle dark/light mode"):
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    
    return st.session_state.theme

def render_bias_card(result):
    """Render bias verdict card"""
    # Determine card color based on verdict
    if "NOT BIASED" in result["verdict"]:
        card_color = "rgba(76, 175, 80, 0.1)"
        border_color = "#4CAF50"
    elif "POTENTIALLY BIASED" in result["verdict"]:
        card_color = "rgba(255, 193, 7, 0.1)"
        border_color = "#FFC107"
    else:
        card_color = "rgba(244, 67, 54, 0.1)"
        border_color = "#F44336"
    
    st.markdown(f"""
    <div style="background-color: {card_color}; border-radius: 10px; padding: 1.5rem; 
                margin: 1rem 0; border-left: 5px solid {border_color}; border: 1px solid {border_color}40;">
        <h3 style="margin-top: 0; color: {border_color};">🧭 Bias Assessment Verdict</h3>
        <div style="display: flex; align-items: center; margin: 15px 0;">
            <div style="font-size: 2.5rem; margin-right: 15px;">📊</div>
            <div>
                <h2 style="margin: 0; color: {border_color};">{result["verdict"]}</h2>
                <p style="margin: 5px 0; font-size: 1.2rem;">Bias Level: <strong>{result["bias_percentage"]}%</strong></p>
            </div>
        </div>
        <div style="background-color: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 5px; margin-top: 10px;">
            <p style="margin: 0;"><strong>📝 Note:</strong> {result["reason"]}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_explanation(result, is_supervised=True):
    """Render explanation of the bias assessment"""
    with st.expander("📖 Understanding the Assessment", expanded=False):
        if is_supervised:
            st.markdown("""
            ### 🔍 How We Assess Bias
            
            **1. Representation Bias**  
            Checks if any demographic group is underrepresented.
            
            **2. Label Bias**  
            Examines differences in positive outcome rates.
            
            **3. Historical Bias**  
            Identifies past societal inequalities.
            
            **4. Statistical Parity**  
            Measures equal distribution of favorable outcomes.
            
            **5. Disparate Impact**  
            Calculates outcome ratios between groups.
            """)
        else:
            st.markdown("""
            ### 🔍 Unsupervised Bias Assessment
            
            Only **Representation Bias** can be assessed without labels.
            
            **Thresholds:**
            - **Balanced**: ≥ 40% representation
            - **Moderate Risk**: 30-40%
            - **High Risk**: < 30%
            
            **Limitations:** Cannot assess outcome fairness without labels.
            """)

def render_traffic_light_legend():
    """Render traffic light visualization"""
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 20px; margin: 1rem 0; flex-wrap: wrap;">
        <div style="text-align: center; padding: 10px; border-radius: 8px; background-color: #f8f9fa; 
                    border: 2px solid #e0e0e0; min-width: 100px;">
            <div style="width: 30px; height: 30px; background-color: #4CAF50; border-radius: 50%; 
                        margin: 0 auto 10px auto;"></div>
            <div><strong>Low Bias</strong></div>
            <small>&lt; 30%</small>
        </div>
        <div style="text-align: center; padding: 10px; border-radius: 8px; background-color: #f8f9fa; 
                    border: 2px solid #e0e0e0; min-width: 100px;">
            <div style="width: 30px; height: 30px; background-color: #FFC107; border-radius: 50%; 
                        margin: 0 auto 10px auto;"></div>
            <div><strong>Moderate</strong></div>
            <small>30-60%</small>
        </div>
        <div style="text-align: center; padding: 10px; border-radius: 8px; background-color: #f8f9fa; 
                    border: 2px solid #e0e0e0; min-width: 100px;">
            <div style="width: 30px; height: 30px; background-color: #F44336; border-radius: 50%; 
                        margin: 0 auto 10px auto;"></div>
            <div><strong>High Bias</strong></div>
            <small>&gt; 60%</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_representation_table(rep_df, min_rep):
    """Render representation table"""
    html_table = """
    <div style="overflow-x: auto; margin: 20px 0;">
        <table style="width: 100%; border-collapse: collapse; background-color: white; border-radius: 8px; overflow: hidden;">
            <thead>
                <tr style="background-color: #87CEEB; color: white;">
                    <th style="padding: 12px; text-align: left;">Group</th>
                    <th style="padding: 12px; text-align: left;">Count</th>
                    <th style="padding: 12px; text-align: left;">Proportion</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in rep_df.iterrows():
        html_table += f"""
            <tr style="border-bottom: 1px solid #e0e0e0;">
                <td style="padding: 10px 12px;"><strong>{row['group']}</strong></td>
                <td style="padding: 10px 12px;">{int(row['count'])}</td>
                <td style="padding: 10px 12px;">{row['proportion']:.1%}</td>
            </tr>
        """
    
    html_table += """
            </tbody>
        </table>
    </div>
    """
    
    st.markdown(html_table, unsafe_allow_html=True)

def render_metric_cards(metrics_dict):
    """Render metric cards in a grid"""
    cols = st.columns(len(metrics_dict))
    
    for idx, (title, value) in enumerate(metrics_dict.items()):
        with cols[idx]:
            # Determine color based on value
            if title == "Min Representation":
                color = "#4CAF50" if value >= 0.4 else "#FFC107" if value >= 0.3 else "#F44336"
            elif "Bias" in title or "Difference" in title:
                color = "#4CAF50" if value < 0.1 else "#FFC107" if value < 0.2 else "#F44336"
            else:
                color = "#87CEEB"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background-color: {color}20; 
                        border-radius: 8px; border: 1px solid {color}40; margin: 5px;">
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">{title}</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: {color};">{value:.3f}</div>
            </div>
            """, unsafe_allow_html=True)