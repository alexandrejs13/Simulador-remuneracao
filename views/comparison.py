import streamlit as st
import pandas as pd
import altair as alt
from src.config import DATA
from src.calculations import get_net_salary
from src.utils import fmt_money, fmt_percent

def render_page(T: dict):
    st.title(T.get("menu_comp_paises", "Comparativo Países"))
    st.caption("Comparativo utilizando valores nominais (sem conversão cambial)")

    c1, c2 = st.columns(2)
    base_salary = c1.number_input("Salário Base Mensal (Nominal)", 10000.0, step=500.0, format="%.2f")
    base_bonus = c2.number_input("Bônus Anual (Nominal)", 0.0, step=500.0, format="%.2f")
    selected_countries = st.multiselect("Países", list(DATA.countries.keys()), default=["Brasil", "Estados Unidos"])
    if not selected_countries: return

    comp_data, chart_data = [], []

    for c in selected_countries:
        sym = DATA.countries[c].get("symbol", "$")
        res = get_net_salary(c, base_salary, other_deductions=0, bonus_annual=base_bonus)
        months = DATA.country_tables["REMUN_MONTHS"].get(c, 12.0)
        annual_gross = (base_salary * months) + base_bonus
        eff_rate = (res["total_deductions"] / res["total_earnings"]) if res["total_earnings"] > 0 else 0.0
        annual_net_est = annual_gross * (1.0 - eff_rate)

        comp_data.append({
            "País": f"{DATA.countries[c].get('flag','')} {c}",
            "Bruto Mensal": fmt_money(base_salary, sym),
            "Líquido Mensal": fmt_money(res["net_salary"], sym),
            "Taxa Efetiva": fmt_percent(eff_rate),
            "Bruto Anual Est.": fmt_money(annual_gross, sym),
            "Líquido Anual Est.": fmt_money(annual_net_est, sym)
        })
        chart_data.extend([{"País":c, "Tipo":"Líquido", "Valor":res["net_salary"]}, 
                           {"País":c, "Tipo":"Impostos/Ded.", "Valor":res["total_deductions"]}])
    
    tab1, tab2 = st.tabs(["📊 Visão Geral", "📈 Gráfico"])
    with tab1: st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
    with tab2:
        chart = alt.Chart(pd.DataFrame(chart_data)).mark_bar().encode(
            x=alt.X('Valor', stack='normalize', axis=alt.Axis(format='%'), title="Distribuição %"),
            y=alt.Y('País'),
            color=alt.Color('Tipo', scale=alt.Scale(domain=['Líquido', 'Impostos/Ded.'], range=['#4CAF50', '#F44336'])),
            tooltip=['País', 'Tipo', alt.Tooltip('Valor', format=',.2f')]
        ).properties(height=100 + len(selected_countries)*30)
        st.altair_chart(chart, use_container_width=True)
