import json
import os
from pathlib import Path
import streamlit as st

class DataLoader:
    """Gerenciador central de dados carregados dos JSONs."""
    def __init__(self):
        # Encontra o diretório 'data' subindo um nível do 'src'
        self.base_path = Path(__file__).resolve().parent.parent / "data"
        
        # Carregamento ansioso de todos os dados essenciais
        self.i18n = self._load("i18n.json", default={"Português": {"sidebar_title": "Carregando..."}})
        self.countries = self._load("countries.json")
        self.country_tables = self._load("country_tables.json")
        self.sti_config = self._load("sti_config.json")
        
        # Tabelas específicas
        self.br_inss = self._load("br_inss.json")
        self.br_irrf = self._load("br_irrf.json")
        self.us_rates = self._load("us_state_tax_rates.json")
        self.regras_fiscais = self._load("regras_fiscais.json") # Carrega este também, se for usar
        
        # --- CORREÇÃO (Erro de KeyError) ---
        # Expõe as chaves do STI no nível superior para fácil acesso
        self.STI_RANGES = self.sti_config.get("STI_RANGES", {})
        self.STI_LEVEL_OPTIONS = self.sti_config.get("STI_LEVEL_OPTIONS", {})
        # --- FIM DA CORREÇÃO ---

    @st.cache_data
    def _load(self, filename: str, default=None) -> dict:
        """Carrega um arquivo JSON da pasta 'data'."""
        try:
            with open(self.base_path / filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            # Mostra um erro claro no app se um arquivo essencial falhar
            st.error(f"Erro Crítico: Não foi possível carregar {filename}. Verifique a pasta 'data'. Detalhe: {e}")
            if default is not None:
                return default
            return {}

# Instância global única (Singleton)
DATA = DataLoader()

# Constantes Globais de Negócio
ANNUAL_CAPS = {
    "US_FICA": 168600.0,
    "US_SUTA_BASE": 7000.0,
    "CA_CPP_YMPEx1": 68500.0,
    "CA_CPP_YMPEx2": 73200.0,
    "CA_CPP_EXEMPT": 3500.0,
    "CA_EI_MIE": 63200.0,
    "MX_UMA_MONTHLY": 3300.53 # 25 * 108.57 (UMA 2024)
}
