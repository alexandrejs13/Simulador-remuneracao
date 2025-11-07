import streamlit as st
import pandas as pd
from src.config import DATA

def render_tables_page(T: dict):
    st.title(T["menu_tables"])
    country = st.selectbox("Selecione o País para visualizar as regras", list(DATA.countries.keys()))
    
    st.header(f"{DATA.countries[country].get('flag','')} {country}")
    
    # Tenta mostrar regras fiscais detalhadas se existirem
    regras = DATA.regras_fiscais.get(country, {}).get("pt", {}).get("regras")
    if regras:
        for r in regras:
            with st.expander(f"📘 {r['tipo']}"):
                st.write(r['explicacao'])
                if 'faixas' in r and r['faixas']:
                    st.table(pd.DataFrame(r['faixas']))
    else:
        # Fallback para mostrar os dados brutos dos outros JSONs
        if country == "Brasil":
            st.subheader("INSS")
            st.json(DATA.br_inss)
            st.subheader("IRRF")
            st.json(DATA.br_irrf)
        elif country == "Estados Unidos":
            st.subheader("State Tax Rates")
            st.write(DATA.us_rates)
        
        # Mostra encargos do empregador
        encargos = DATA.country_tables["EMPLOYER_COST"].get(country)
        if encargos:
            st.subheader("Encargos Empregador (Geral)")
            st.dataframe(pd.DataFrame(encargos))

def render_sti_page(T: dict):
    st.title(T["menu_sti_rules"])
    st.markdown("Targets de Bônus por Nível e Área.")
    
    ranges = DATA.sti_config.get("STI_RANGES", {})
    for area, levels in ranges.items():
        st.subheader(area)
        df = pd.DataFrame([(k, f"{v[0]*100:.0f}% - {v[1]*100:.0f}%") for k,v in levels.items()], columns=["Nível", "Target Range"])
        st.table(df)
