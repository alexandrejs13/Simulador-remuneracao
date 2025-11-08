import streamlit as st
import pandas as pd
from src.config import DATA
from src.calculations import get_net_salary, get_sti_targets
from src.utils import fmt_money, money_or_blank, INPUT_FORMAT
from src.styles import card

def render_page(T: dict):
    st.title(T.get("title_calc", "Simulador"))

    # 1. SELEÇÃO DE PAÍS
    country_list = list(DATA.countries.keys())
    idx = 0
    if 'last_country' in st.session_state and st.session_state.last_country in country_list:
        idx = country_list.index(st.session_state.last_country)
    
    col_c1, col_c2 = st.columns([0.15, 0.85])
    flag = DATA.countries.get(country_list[idx], {}).get("flag", "")
    col_c1.markdown(f"<div class='country-header'>{flag}</div>", unsafe_allow_html=True)
    country = col_c2.selectbox(T.get("country", "País"), country_list, index=idx, key="calc_country_sel")
    st.session_state.last_country = country
    sym = DATA.countries[country].get("symbol", "$")

    # 2. PARÂMETROS EM ABAS
    tab_fixed, tab_variable = st.tabs([T.get("tab_fixed", "Fixo"), T.get("tab_variable", "Variável")])
    dependents, state_rate, state_name = 0, 0.0, ""
    
    with tab_fixed:
        c1, c2, c3 = st.columns(3)
        salary = c1.number_input(f"{T.get('salary','Salário')} ({sym})", 0.0, value=10000.0, step=500.0, format=INPUT_FORMAT)
        if country == "Brasil":
            dependents = c2.number_input(T.get("dependents", "Dependentes"), 0, value=0, step=1)
            other_deductions = c3.number_input(f"{T.get('other_deductions','Outras Ded.')} ({sym})", 0.0, step=50.0, format=INPUT_FORMAT)
        elif country == "Estados Unidos":
            state_name = c2.selectbox(T.get("state", "Estado"), options=list(DATA.us_rates.keys()), key='us_state_sel')
            state_rate = DATA.us_rates.get(state_name, 0.0)
            c2.caption(f"Taxa: {state_rate*100:.2f}%")
            other_deductions = c3.number_input(f"{T.get('other_deductions','Outras Ded.')} ({sym})", 0.0, step=50.0, format=INPUT_FORMAT)
        else:
             other_deductions = c2.number_input(f"{T.get('other_deductions','Outras Ded.')} ({sym})", 0.0, step=50.0, format=INPUT_FORMAT)

    with tab_variable:
        c1, c2 = st.columns(2)
        bonus = c1.number_input(f"{T.get('bonus','Bônus Anual')} ({sym})", 0.0, step=1000.0, format=INPUT_FORMAT)
        
        # --- CORREÇÃO (KeyError) ---
        sti_areas = list(DATA.STI_LEVEL_OPTIONS.keys())
        # --- FIM DA CORREÇÃO ---

        area = c2.selectbox(T.get("area", "Área STI"), sti_areas, key='sti_area_sel')
        levels = DATA.STI_LEVEL_OPTIONS.get(area, [])
        level = c2.selectbox(T.get("level", "Nível STI"), levels, index=len(levels)-1 if levels else 0, key='sti_level_sel')

        c_chk1, c_chk2 = st.columns(2)
        incide_medias = False
        if country == "Brasil":
            incide_medias = c_chk1.checkbox(T.get("lbl_incide_medias", "Incide Médias?"), value=False)
        
        sti_min, sti_max = get_sti_targets(area, level)
        
        # Safe access to REMUN_MONTHS with fallback and validation
        raw_months = None
        if hasattr(DATA, 'tables') and isinstance(DATA.tables, dict):
            raw_months = DATA.tables.get('REMUN_MONTHS', {}).get(country)
        if raw_months is None and hasattr(DATA, 'country_tables') and isinstance(DATA.country_tables, dict):
            raw_months = DATA.country_tables.get('REMUN_MONTHS', {}).get(country)
        
        # Normalize to integer >= 1
        try:
            months = int(raw_months)
            if months < 1:
                raise ValueError()
        except Exception:
            months = 12
            st.warning(f"Chave REMUN_MONTHS ausente ou inválida para {country}. Usando {months} meses como padrão.")
        
        annual_sal = salary * months
        actual_sti = (bonus / annual_sal) if annual_sal > 0 else 0.0
        in_target = (sti_min <= actual_sti <= sti_max) if level != "Others" else (actual_sti <= sti_max)
        status_color = "green" if in_target else "red"
        st.markdown(f"**Target STI:** {sti_min*100:.0f}% - {sti_max*100:.0f}% | **Atual:** <span style='color:{status_color}'>{actual_sti*100:.1f}%</span>", unsafe_allow_html=True)

    st.divider()

    # --- 3. RESULTADOS ---
    res = get_net_salary(country, salary, dependents=dependents, other_deductions=other_deductions, 
                         state_rate=state_rate, state_name=state_name, 
                         bonus_annual=bonus, incide_medias=incide_medias)

    st.subheader(T.get("monthly_comp_title", "Mensal"))
    c1, c2, c3 = st.columns(3)
    c1.markdown(card(T.get("tot_earnings", "Proventos"), fmt_money(res["total_earnings"], sym), "earn"), unsafe_allow_html=True)
    c2.markdown(card(T.get("tot_deductions", "Descontos"), fmt_money(res["total_deductions"], sym), "ded"), unsafe_allow_html=True)
    c3.markdown(card(T.get("net", "Líquido"), fmt_money(res["net_salary"], sym), "net"), unsafe_allow_html=True)
    if country == "Brasil" and res["fgts"] > 0:
        st.caption(f"💼 {T.get('fgts_deposit', 'FGTS')}: {fmt_money(res['fgts'], sym)}")

    # Tabela de Detalhamento
    rows_html = ""
    for desc, earn, ded in res["lines"]:
        rows_html += f"<tr><td>{desc}</td><td style='color:green;text-align:right;'>{money_or_blank(earn, sym)}</td><td style='color:red;text-align:right;'>{money_or_blank(ded, sym)}</td></tr>"
    
    st.markdown(f"""
    <table class="styled-table">
        <thead><tr><th>{T.get("rules_table_desc", "Descrição")}</th><th>{T.get("earnings", "Proventos")}</th><th>{T.get("deductions", "Descontos")}</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader(T.get("annual_comp_title", "Anual"))
    annual_total = (salary * months) + bonus
    ac1, ac2, ac3 = st.columns(3)
    ac1.metric(T.get("annual_salary", "Sal. Anual"), fmt_money(annual_sal, sym), help=f"{months} meses")
    ac2.metric(T.get("annual_bonus", "Bônus"), fmt_money(bonus, sym))
    ac3.metric(T.get("annual_total", "Total"), fmt_money(annual_total, sym))
