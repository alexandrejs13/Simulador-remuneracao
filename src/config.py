import json
import os
from pathlib import Path
import streamlit as st

class DataLoader:
    """Gerenciador central de dados carregados dos JSONs."""
    def __init__(self):
        self.base_path = Path(os.getcwd()) / "data"
        # Carregamento ansioso de todos os dados essenciais
        self.i18n = self._load("i18n.json")
        self.countries = self._load("countries.json")
        self.country_tables = self._load("country_tables.json")
        self.sti_config = self._load("sti_config.json")
        
        # Tabelas específicas
        self.br_inss = self._load("br_inss.json")
        self.br_irrf = self._load("br_irrf.json")
        self.us_rates = self._load("us_state_tax_rates.json")
        self.regras_fiscais = self._load("regras_fiscais.json")

    def _load(self, filename: str) -> dict:
        try:
            with open(self.base_path / filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Em produção, isso deveria logar um erro grave.
            # Para este exemplo, retorna vazio para não quebrar tudo imediatamente.
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
    "MX_UMA_MONTHLY": 3300.53 # Valor aproximado de 25 UMA mensal para teto
}
