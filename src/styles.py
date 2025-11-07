import streamlit as st

def apply_global_styles():
    st.markdown("""
    <style>
        /* Layout Principal */
        .main .block-container { max-width: 1200px; padding: 2rem 1rem; }
        h1, h2, h3, h4, h5 { color: #0e1117; font-family: 'Segoe UI', sans-serif; }
        h1 { border-bottom: 2px solid #f0f2f6; padding-bottom: 10px; }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa; border-right: 1px solid #dee2e6;
        }
        section[data-testid="stSidebar"] h2 { color: #0a3d62 !important; font-size: 1.5rem !important; }
        section[data-testid="stSidebar"] .stRadio > div { gap: 0.25rem; }
        section[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] { 
            padding: 0.5rem 0.75rem; margin: 0; border-radius: 0.375rem; 
            transition: background-color 0.2s;
        }
        section[data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:has(input:checked) {
            background-color: #0a3d62; color: white !important;
        }
        section[data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:has(input:checked) span {
            color: white !important; font-weight: 600;
        }

        /* Cards de Métricas */
        .metric-container {
            background-color: white; border: 1px solid #e0e0e0; border-radius: 8px;
            padding: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .metric-container:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .metric-label { color: #666; font-size: 0.9rem; text-transform: uppercase; }
        .metric-value { color: #0a3d62; font-size: 1.8rem; font-weight: 700; margin-top: 5px; }
        
        .bg-earn { border-left: 5px solid #4CAF50; }
        .bg-ded { border-left: 5px solid #F44336; }
        .bg-net { border-left: 5px solid #2196F3; }

        /* Tabelas */
        .styled-table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.95rem; box-shadow: 0 0 20px rgba(0, 0, 0, 0.05); border-radius: 8px 8px 0 0; overflow: hidden; }
        .styled-table thead tr { background-color: #0a3d62; color: #ffffff; text-align: left; }
        .styled-table th, .styled-table td { padding: 12px 15px; }
        .styled-table tbody tr { border-bottom: 1px solid #dddddd; }
        .styled-table tbody tr:nth-of-type(even) { background-color: #f3f3f3; }
        .styled-table tbody tr:last-of-type { border-bottom: 2px solid #0a3d62; font-weight: bold; }

        /* Abas */
        .stTabs [data-baseweb="tab-list"] { gap: 4px; }
        .stTabs [data-baseweb="tab"] {
            height: 45px; white-space: pre-wrap; background-color: #e9ecef;
            border-radius: 5px 5px 0 0; gap: 1px; padding: 10px 20px; border: none;
        }
        .stTabs [aria-selected="true"] { background-color: #fff; border-top: 3px solid #0a3d62; }
        .country-header { font-size: 4rem; text-align: left; margin-top: -20px; }
        .card-row-spacing { margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

def card(label, value, type="neutral"):
    """Gera o HTML para um card de métrica estilizado."""
    bg_class = {"earn": "bg-earn", "ded": "bg-ded", "net": "bg-net"}.get(type, "")
    return f"""
    <div class="metric-container {bg_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
