"""
Urban Mobility Analytics – Dashboard Streamlit principal
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st

st.set_page_config(
    page_title="Urban Mobility Analytics | Argentina",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%);
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stRadio label { 
    padding: 8px 12px; border-radius: 8px; transition: background .2s;
}
section[data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,.08); }

/* Main background */
.main .block-container { padding-top: 2rem; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid rgba(99,179,237,.2);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    color: #f1f5f9;
}
.metric-card .label { font-size: .8rem; color: #94a3b8; font-weight: 500; letter-spacing: .05em; text-transform: uppercase; }
.metric-card .value { font-size: 2rem; font-weight: 700; color: #38bdf8; margin: .25rem 0; }
.metric-card .delta { font-size: .85rem; color: #4ade80; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #8b5cf6 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    color: white;
    margin-bottom: 1.5rem;
}
.hero h1 { font-size: 2rem; font-weight: 700; margin: 0 0 .4rem; }
.hero p  { font-size: 1rem; opacity: .9; margin: 0; }
</style>
""", unsafe_allow_html=True)

# ── Language Selector ────────────────────────────────────────────────
from dashboard.components.translations import t

with st.sidebar:
    st.markdown("### 🚌 Urban Mobility")
    st.markdown("**Argentina SUBE + GTFS**")
    st.markdown("---")
    
    # Language Toggle
    lang_choice = st.radio(
        "🌐 Language / Idioma",
        options=["Español", "English"],
        index=0,
        horizontal=True
    )
    st.session_state["lang"] = "es" if lang_choice == "Español" else "en"
    st.markdown("---")

    # Translated Navigation Map
    pages_map = {
        t("nav_overview"): "overview",
        t("nav_demand"): "demand",
        t("nav_network"): "network",
        t("nav_spatial"): "spatial"
    }
    
    selected_page_label = st.radio(
        t("nav_title"),
        options=list(pages_map.keys()),
        label_visibility="collapsed"
    )
    page = pages_map[selected_page_label]
    
    st.markdown("---")
    st.markdown(f"<small style='color:#64748b'>{t('footer_data')}</small>", unsafe_allow_html=True)

# ── Page routing ─────────────────────────────────────────────────────
if page == "overview":
    from dashboard.views import overview; overview.render()
elif page == "demand":
    from dashboard.views import demand; demand.render()
elif page == "network":
    from dashboard.views import network; network.render()
elif page == "spatial":
    from dashboard.views import spatial; spatial.render()
