import sys
import os
import streamlit as st
import pandas as pd
import altair as alt

# --- INÍCIO DA CORREÇÃO ---
# Adiciona o diretório do projeto ao path do Python
# Isso força o app.py a "enxergar" as pastas 'src' e 'views'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
# --- FIM DA CORREÇÃO ---

from src.config import DATA
from src.styles import apply_global_styles, card
from src.utils import fmt_currency, money_or_blank, fmt_percent
from src.calculations import (
    get_net_salary, get_employer_cost, get_sti_targets
)
from views import calculator, comparison, cost_comparison, info

# Configuração Inicial da Página
st.set_page_config(page_title="Simulador de Remuneração", layout="wide", page_icon="💰")
apply_global_styles()

# Inicialização de Estado (Define o idioma padrão)
if 'locale' not in st.session_state: 
    st.session_state.locale = 'Português'

# --- SIDEBAR DE NAVEGAÇÃO ---
with st.sidebar:
    # Carrega o dicionário de tradução (Locale)
    # Usamos .get() para evitar KeyErrors se o JSON estiver incompleto
    T = DATA.i18n.get(st.session_state.locale, DATA.i18n.get('Português', {}))
    
    # Header Sidebar
    st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><h2>{T.get('sidebar_title', 'Simulador')}</h2></div>", unsafe_allow_html=True)
    
    # Seletor de Idioma
    col_l1, col_l2 = st.columns([0.3, 0.7])
    col_l1.write(f"<div style='margin-top: 15px; font-size: 20px;'>🌐</div>", unsafe_allow_html=True)
    lang_options = list(DATA.i18n.keys())
    try:
        lang_index = lang_options.index(st.session_state.locale)
    except ValueError:
        lang_index = 0 # Default para Português se a chave não existir
        
    new_lang = col_l2.selectbox("Language", options=lang_options, 
                               index=lang_index, 
                               label_visibility="collapsed")
    if new_lang != st.session_state.locale:
        st.session_state.locale = new_lang
        st.rerun()

    st.markdown("---")

    # Menu Principal (Robusto com .get())
    key_sim = T.get('menu_sim', 'Simulador de Remuneração')
    key_comp_paises = T.get('menu_comp_paises', 'Comparativo entre Países')
    key_comp_cost = T.get('menu_comp_cost', 'Comparativo Custo Empregador')
    key_tables = T.get('menu_tables', 'Tabelas de Contribuições')
    key_sti_rules = T.get('menu_sti_rules', 'Regras de Cálculo do STI')

    MENU_OPTIONS = [
        "📌 " + key_sim,
        "🌍 " + key_comp_paises,
        "🏢 " + key_comp_cost,
        "---", # Separador
        "📊 " + key_tables,
        "📈 " + key_sti_rules
    ]

    MENU_MAP = {
        "📌 " + key_sim: "calc_sim",
        "🌍 " + key_comp_paises: "comp_countries",
        "🏢 " + key_comp_cost: "comp_cost",
        "📊 " + key_tables: "info_tables",
        "📈 " + key_sti_rules: "info_sti"
    }

    selected_label = st.radio("Navegação Principal", MENU_OPTIONS, label_visibility="collapsed", 
                              format_func=lambda x: "" if x == "---" else x)
    
    if selected_label == "---":
        current_page = st.session_state.get('last_page', 'calc_sim') # Mantém a página ou vai pro padrão
    else:
        current_page = MENU_MAP.get(selected_label, "calc_sim")
        st.session_state.last_page = current_page # Salva a última seleção válida

    st.markdown("---")
    st.caption(f"v2025.11.07 | {st.session_state.locale}")

# --- ROTEAMENTO DE VIZUALIZAÇÕES ---
# O 'T' (dicionário de tradução) é passado para cada página
if current_page == "calc_sim":
    calculator.render_page(T)
elif current_page == "comp_countries":
    comparison.render_page(T)
elif current_page == "comp_cost":
    cost_comparison.render_page(T)
elif current_page == "info_tables":
    info.render_tables_page(T)
elif current_page == "info_sti":
    info.render_sti_page(T)
