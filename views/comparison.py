import streamlit as st
import pandas as pd
import altair as alt
from src.config import DATA
from src.calculations import get_net_salary
from src.utils import fmt_currency, fmt_percent

def render_page(T: dict):
    st.title(T["menu_comp_paises"])
    st.caption("Comparativo utilizando valores nominais (sem conversão cambial)")

    c1, c2 = st.columns(2)
    base_salary = c1.number_input("Salário Base Mensal (Nominal)", value=10000.0, step=500.0, format="%.2f")
    base_bonus = c2.number_input("Bônus Anual (Nominal)", value=0.0, step=500.0, format="%.2f")

    selected_countries = st.multiselect("Selecione os Países", list(DATA.countries.keys()), default=["Brasil", "Estados Unidos", "México"])

    if not selected_countries:
        st.warning("Selecione pelo menos um país para comparar.")
        return

    comparison_data = []
    chart_data = []

    for country in selected_countries:
        sym = DATA.countries[country].get("symbol", "$")
        # Usa defaults (sem dependentes, sem taxas estaduais específicas) para comparação generalista
        res = get_net_salary(country, base_salary, bonus_annual=base_bonus)
        
        months = DATA.country_tables["REMUN_MONTHS"].get(country, 12.0)
        annual_gross = (base_salary * months) + base_bonus
        
        # Taxa efetiva sobre o mensal recorrente
        effective_rate = (res["total_deductions"] / res["total_earnings"]) if res["total_earnings"] > 0 else 0.0
        # Estimativa anual líquida simples
        annual_net_est = annual_gross * (1.0 - effective_rate)

        comparison_data.append({
            "País": f"{DATA.countries[country].get('flag','')} {country}",
            "Bruto Mensal": fmt_currency(base_salary, sym),
            "Líquido Mensal": fmt_currency(res["net_salary"], sym),
            "Taxa Efetiva": fmt_percent(effective_rate),
            "Bruto Anual Est.": fmt_currency(annual_gross, sym),
            "Líquido Anual Est.": fmt_currency(annual_net_est, sym)
        })

        # Dados para o gráfico (normalizados para moeda base se quiser, aqui nominal)
        chart_data.append({"País": country, "Tipo": "Líquido", "Valor": res["net_salary"]})
        chart_data.append({"País": country, "Tipo": "Impostos/Ded.", "Valor": res["total_deductions"]})

    # Tabela
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

    # Gráfico
    st.subheader("Comparativo Visual (Mensal)")
    chart = alt.Chart(pd.DataFrame(chart_data)).mark_bar().encode(
        x=alt.X('Valor', stack='normalize', axis=alt.Axis(format='%'), title="Distribuição %"),
        y=alt.Y('País'),
        color=alt.Color('Tipo', scale=alt.Scale(domain=['Líquido', 'Impostos/Ded.'], range=['#4CAF50', '#F44336'])),
        tooltip=['País', 'Tipo', alt.Tooltip('Valor', format=',.2f')]
    ).properties(height=100 + len(selected_countries)*30)
    
    st.altair_chart(chart, use_container_width=True)
