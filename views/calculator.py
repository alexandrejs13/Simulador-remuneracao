import streamlit as st
import pandas as pd
from src.config import DATA
from src.calculations import get_net_salary, get_sti_targets
from src.utils import fmt_currency
from src.styles import card

def render_page(T: dict):
    st.title(T["title_calc"])

    # --- 1. SELEÇÃO DE PAÍS (Topo da página) ---
    country_list = list(DATA.countries.keys())
    # Tenta manter o país selecionado entre navegações
    idx = country_list.index(st.session_state.get('last_country', 'Brasil')) if st.session_state.get('last_country') in country_list else 0
    
    col_c1, col_c2 = st.columns([0.2, 0.8])
    with col_c1:
        flag = DATA.countries[country_list[idx]].get("flag", "")
        st.markdown(f"<h1 style='text-align:center; border:none; font-size: 4rem;'>{flag}</h1>", unsafe_allow_html=True)
    with col_c2:
        country = st.selectbox(T["country"], country_list, index=idx, key="calc_country_sel")
        st.session_state.last_country = country

    sym = DATA.countries[country].get("symbol", "$")

    # --- 2. PARÂMETROS EM ABAS ---
    tab_fixed, tab_variable = st.tabs([T["tab_fixed"], T["tab_variable"]])

    # Valores padrão para evitar erros de referência antes da atribuição
    dependents, state_rate, state_name = 0, 0.0, ""
    
    with tab_fixed:
        c1, c2, c3 = st.columns(3)
        salary = c1.number_input(f"{T['salary']} ({sym})", min_value=0.0, value=10000.0, step=500.0, format="%.2f")
        
        if country == "Brasil":
            dependents = c2.number_input(T["dependents"], min_value=0, step=1)
            other_deductions = c3.number_input(f"{T['other_deductions']} ({sym})", min_value=0.0, step=50.0, format="%.2f")
        elif country == "Estados Unidos":
            state_name = c2.selectbox(T["state"], options=list(DATA.us_rates.keys()))
            state_rate = DATA.us_rates.get(state_name, 0.0)
            c2.caption(f"Tax Rate: {state_rate*100:.2f}%")
            other_deductions = c3.number_input(f"{T['other_deductions']} ({sym})", min_value=0.0, step=50.0, format="%.2f")
        else:
            # Layout genérico para outros países
            other_deductions = c2.number_input(f"{T['other_deductions']} ({sym})", min_value=0.0, step=50.0, format="%.2f")

    with tab_variable:
        c1, c2 = st.columns(2)
        bonus = c1.number_input(f"{T['bonus']} ({sym})", min_value=0.0, step=1000.0, format="%.2f")
        
        # STI Configs
        sti_areas = list(DATA.sti_config["STI_LEVEL_OPTIONS"].keys())
        area = c2.selectbox(T["area"], sti_areas)
        levels = DATA.sti_config["STI_LEVEL_OPTIONS"].get(area, [])
        level = c2.selectbox(T["level"], levels)

        # Checkboxes de controle
        c_chk1, c_chk2 = st.columns(2)
        incide_medias = False
        if country == "Brasil":
            incide_medias = c_chk1.checkbox(T["lbl_incide_medias"], value=False)
        
        # Mostra target STI
        sti_min, sti_max = get_sti_targets(area, level)
        months = DATA.country_tables["REMUN_MONTHS"].get(country, 12.0)
        annual_sal = salary * months
        actual_sti = (bonus / annual_sal) if annual_sal > 0 else 0.0
        
        in_target = (sti_min <= actual_sti <= sti_max) if level != "Others" else (actual_sti <= sti_max)
        status_color = "green" if in_target else "red"
        st.markdown(f"**Target STI:** {sti_min*100:.0f}% - {sti_max*100:.0f}% | **Atual:** <span style='color:{status_color}'>{actual_sti*100:.1f}%</span>", unsafe_allow_html=True)

    st.markdown("---")

    # --- 3. RESULTADOS (Cálculo e Exibição) ---
    res = get_net_salary(country, salary, dependents=dependents, other_deductions=other_deductions, 
                         state_rate=state_rate, state_name=state_name, 
                         bonus_annual=bonus, incide_medias=incide_medias)

    # Cards Principais
    c1, c2, c3 = st.columns(3)
    c1.markdown(card(T["tot_earnings"], fmt_currency(res["total_earnings"], sym), "earn"), unsafe_allow_html=True)
    c2.markdown(card(T["tot_deductions"], fmt_currency(res["total_deductions"], sym), "ded"), unsafe_allow_html=True)
    c3.markdown(card(T["net"], fmt_currency(res["net_salary"], sym), "net"), unsafe_allow_html=True)

    if country == "Brasil" and res["fgts"] > 0:
        st.caption(f"💼 {T['fgts_deposit']}: {fmt_currency(res['fgts'], sym)}")

    # Tabela de Detalhamento (Usando HTML puro para estilo controle total)
    rows_html = ""
    for desc, earn, ded in res["lines"]:
        rows_html += f"<tr><td>{desc}</td><td style='color:green'>{fmt_currency(earn, sym) if earn > 0 else ''}</td><td style='color:red'>{fmt_currency(ded, sym) if ded > 0 else ''}</td></tr>"
    
    table_html = f"""
    <table class="styled-table">
        <thead><tr><th>Descrição</th><th>Proventos</th><th>Descontos</th></tr></thead>
        <tbody>
            {rows_html}
            <tr style="font-weight:bold; background-color:#eef;">
                <td>TOTAIS</td>
                <td>{fmt_currency(res["total_earnings"], sym)}</td>
                <td>{fmt_currency(res["total_deductions"], sym)}</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    # Visão Anual Simplificada
    st.subheader(T["annual_comp_title"])
    ac1, ac2, ac3 = st.columns(3)
    annual_total = annual_sal + bonus
    ac1.metric(T["annual_salary"], fmt_currency(annual_sal, sym), help=f"Fator: {months} meses")
    ac2.metric(T["annual_bonus"], fmt_currency(bonus, sym))
    ac3.metric(T["annual_total"], fmt_currency(annual_total, sym))
