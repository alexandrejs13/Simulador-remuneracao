import streamlit as st
from src.config import DATA
from src.styles import apply_global_styles
from views import calculator, comparison, cost_comparison, info

# Configuração Inicial da Página
st.set_page_config(page_title="Simulador de Remuneração", layout="wide", page_icon="💰")
apply_global_styles()

# Inicialização de Estado
if 'locale' not in st.session_state: st.session_state.locale = 'Português'

# --- SIDEBAR DE NAVEGAÇÃO ---
with st.sidebar:
    # Header Sidebar
    T = DATA.i18n[st.session_state.locale]
    st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><h2>{T['sidebar_title']}</h2></div>", unsafe_allow_html=True)
    
    # Seletor de Idioma
    col_l1, col_l2 = st.columns([0.3, 0.7])
    col_l1.write(f"<div style='margin-top: 15px; font-size: 20px;'>🌐</div>", unsafe_allow_html=True)
    new_lang = col_l2.selectbox("Language", options=["Português", "English", "Español"], 
                               index=["Português", "English", "Español"].index(st.session_state.locale), 
                               label_visibility="collapsed")
    if new_lang != st.session_state.locale:
        st.session_state.locale = new_lang
        st.rerun()

    st.markdown("---")

    # Menu Principal (Radio customizado para parecer seções)
    MENU_OPTIONS = [
        "📌 " + T['menu_sim'],
        "🌍 " + T['menu_comp_paises'],
        "🏢 " + T['menu_comp_cost'],
        "---", # Separador Lógico
        "📊 " + T['menu_tables'],
        "📈 " + T['menu_sti_rules']
    ]

    # Mapeamento reverso para saber qual página chamar
    MENU_MAP = {
        "📌 " + T['menu_sim']: "calc",
        "🌍 " + T['menu_comp_paises']: "comp_countries",
        "🏢 " + T['menu_comp_cost']: "comp_cost",
        "📊 " + T['menu_tables']: "info_tables",
        "📈 " + T['menu_sti_rules']: "info_sti"
    }

    selected_label = st.radio("Navegação Principal", MENU_OPTIONS, label_visibility="collapsed")
    
    # Tratamento para separadores (se o usuário clicar neles, nada acontece ou volta pro padrão)
    if selected_label == "---":
        current_page = "calc"
    else:
        current_page = MENU_MAP.get(selected_label, "calc")

    st.markdown("---")
    st.caption(f"v2025.11.07 | {st.session_state.locale}")

# --- ROTEAMENTO DE VIZUALIZAÇÕES ---
if current_page == "calc":
    calculator.render_page(T)
elif current_page == "comp_countries":
    comparison.render_page(T)
elif current_page == "comp_cost":
    cost_comparison.render_page(T)
elif current_page == "info_tables":
    info.render_tables_page(T)
elif current_page == "info_sti":
    info.render_sti_page(T)
