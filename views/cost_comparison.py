import streamlit as st
import pandas as pd
from src.config import DATA
from src.calculations import get_employer_cost
from src.utils import fmt_money, fmt_percent

def render_page(T: dict):
    st.title(T.get("menu_comp_cost", "Comparativo Custo Empregador"))

    c1, c2, c3 = st.columns(3)
    salary = c1.number_input("Salário Base Mensal", 10000.0, step=500.0, format="%.2f")
    bonus = c2.number_input("Bônus Anual", 5000.0, step=500.0, format="%.2f")
    incide_bonus = c3.checkbox(T.get("lbl_incide_encargos", "Incide Bônus?"), True)

    countries = st.multiselect("Países", list(DATA.countries.keys()), default=list(DATA.countries.keys())[:3])
    if not countries: return

    summary_list, details_map = [], {}
    all_items = set()

    for c in countries:
        res = get_employer_cost(c, salary, bonus, T, incide_bonus)
        sym = DATA.countries[c].get("symbol", "$")
        
        base_remun = (salary * res["months_factor"]) + bonus
        charge_pct = (res["total_charges"] / base_remun) if base_remun > 0 else 0.0
        
        summary_list.append({
            "País": f"{DATA.countries[c].get('flag','')} {c}",
            "Custo Total Anual": fmt_money(res["total_cost"], sym),
            "Encargos Totais (%)": fmt_percent(charge_pct),
            "Multiplicador (x12 Sal.)": f"{res['multiplier']:.3f}x"
        })
        details_map[c] = {item['Item']: item['Valor'] for item in res['breakdown']}
        all_items.update(details_map[c].keys())

    st.subheader("Resumo Comparativo")
    st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)

    st.subheader("Detalhamento dos Encargos (Valores Anuais)")
    
    detailed_data = []
    for item in sorted(list(all_items)):
        row = {"Encargo": item}
        for c in countries:
            sym = DATA.countries[c].get("symbol", "$")
            row[c] = fmt_money(details_map[c].get(item, 0.0), sym)
        detailed_data.append(row)
        
    st.dataframe(pd.DataFrame(detailed_data), use_container_width=True, hide_index=True)
