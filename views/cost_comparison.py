import streamlit as st
import pandas as pd
from src.config import DATA
from src.calculations import get_employer_cost
from src.utils import fmt_currency

def render_page(T: dict):
    st.title(T["menu_comp_cost"])

    c1, c2, c3 = st.columns(3)
    salary = c1.number_input("Salário Base Mensal", value=10000.0, step=500.0, format="%.2f")
    bonus = c2.number_input("Bônus Anual", value=5000.0, step=500.0, format="%.2f")
    incide_bonus = c3.checkbox(T["lbl_incide_encargos"], value=True, help="Inclui bônus na base de cálculo dos encargos compatíveis.")

    countries = st.multiselect("Países para Comparação", list(DATA.countries.keys()), default=list(DATA.countries.keys())[:3])

    if not countries: return

    summary_list = []
    details_map = {}

    for c in countries:
        res = get_employer_cost(c, salary, bonus, incide_bonus)
        sym = DATA.countries[c].get("symbol", "$")
        
        summary_list.append({
            "País": c,
            "Custo Total Anual": fmt_currency(res["total_cost"], sym),
            "Encargos Totais": fmt_currency(res["total_charges"], sym),
            "Multiplicador (sobre 12x Sal.)": f"{res['multiplier']:.3f}x"
        })
        details_map[c] = res["breakdown"]

    st.subheader("Resumo Comparativo")
    st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)

    st.subheader("Detalhamento dos Encargos")
    # Layout dinâmico de colunas para os detalhes
    cols = st.columns(len(countries))
    for idx, c in enumerate(countries):
        with cols[idx]:
            flag = DATA.countries[c].get("flag", "")
            st.markdown(f"### {flag} {c}")
            if details_map[c]:
                df = pd.DataFrame(details_map[c])
                # Formatação simples para exibição compacta
                st.dataframe(
                    df.style.format({"Valor": "{:,.2f}", "Rate": "{:.2f}%"}), 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={"Valor": st.column_config.NumberColumn(format="$ %.2f")}
                )
            else:
                st.info("Sem encargos cadastrados.")
