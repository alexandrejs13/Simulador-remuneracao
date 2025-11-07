import streamlit as st
import pandas as pd
from src.config import DATA

def render_tables_page(T: dict):
    st.title(T.get("menu_tables", "Tabelas de Contribuições"))
    country = st.selectbox("Selecione o País", list(DATA.countries.keys()))
    
    st.header(f"{DATA.countries[country].get('flag','')} {country}")
    
    if country == "Brasil":
        st.subheader("INSS - Empregado (CLT)")
        st.dataframe(pd.DataFrame(DATA.br_inss.get("faixas", [])))
        st.caption(f"Teto de Contribuição: {DATA.br_inss.get('teto_contribuicao')}")
        st.subheader("IRRF - Empregado (CLT)")
        st.dataframe(pd.DataFrame(DATA.br_irrf.get("faixas", [])))
        st.caption(f"Dedução por Dependente: {DATA.br_irrf.get('deducao_dependente')}")
    elif country == "Estados Unidos":
        st.subheader("Taxas Estaduais (Exemplos)")
        st.dataframe(pd.Series(DATA.us_rates), columns=["Taxa"])
    
    encargos = DATA.country_tables["EMPLOYER_COST"].get(country)
    if encargos:
        st.subheader("Encargos Empregador (Visão Geral)")
        st.dataframe(pd.DataFrame(encargos))
    else:
        st.info("Nenhum encargo detalhado cadastrado para este país.")

def render_sti_page(T: dict):
    st.title(T.get("menu_sti_rules", "Regras STI"))
    st.markdown("Targets de Bônus por Nível e Área.")
    
    # --- CORREÇÃO (KeyError) ---
    ranges = DATA.STI_RANGES
    # --- FIM DA CORREÇÃO ---

    if not ranges:
        st.error("Arquivo sti_config.json não carregado ou está vazio.")
        return

    for area, levels in ranges.items():
        st.subheader(area)
        try:
            df = pd.DataFrame([(k, f"{v[0]*100:.0f}% - {v[1]*100:.0f}%") for k,v in levels.items()], columns=["Nível", "Target Range"])
            st.table(df)
        except Exception as e:
            st.error(f"Erro ao formatar dados STI para '{area}': {e}")
            st.json(levels) # Mostra os dados brutos em caso de erro
