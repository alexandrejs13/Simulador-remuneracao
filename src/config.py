import os
import json
import streamlit as st


class DataLoader:
    """
    Classe responsável por carregar arquivos JSON e parâmetros do app.
    Compatível com Streamlit Cloud e Python 3.13.
    """

    def __init__(self):
        # Defaults convertidos em string (para evitar UnhashableParamError)
        default_i18n = json.dumps({"Português": {"sidebar_title": "Carregando..."}})
        default_empty = "{}"

        # Carregamento dos arquivos
        self.i18n = self._load_json("i18n.json", default_str=default_i18n)
        self.sti_config = self._load_json("sti_config.json", default_str=default_empty)
        self.countries = self._load_json("countries.json", default_str=default_empty)
        self.country_tables = self._load_json("country_tables.json", default_str=default_empty)
        self.us_rates = self._load_json("us_state_tax_rates.json", default_str=default_empty)
        self.br_inss = self._load_json("br_inss.json", default_str=default_empty)
        self.br_irrf = self._load_json("br_irrf.json", default_str=default_empty)

        # Criação dos atributos usados nas views e cálculos
        self.STI_LEVEL_OPTIONS = self._extract_sti_levels()
        self.STI_RANGES = self._extract_sti_ranges()

    # --------------------------------------------------------------------
    # Cache seguro
    # --------------------------------------------------------------------
    @st.cache_data(show_spinner=False)
    def _load_json(_self, filename: str, default_str: str = "{}"):
        """
        Lê arquivo JSON do diretório /data com cache seguro.
        """
        try:
            # Usa caminho absoluto baseado na localização deste arquivo
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base_dir, "data", filename)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return json.loads(default_str)
        except Exception as e:
            st.warning(f"⚠️ Erro ao carregar {filename}: {e}")
            try:
                return json.loads(default_str)
            except Exception:
                return {}

    # --------------------------------------------------------------------
    # Extrai áreas e níveis do STI (ex: Comercial / Corporativo)
    # --------------------------------------------------------------------
    def _extract_sti_levels(self):
        """
        Retorna um dicionário de áreas e níveis do sti_config.json.
        Exemplo:
        {
            "Comercial": {"Analista": 0.10, "Gerente": 0.20},
            "Corporativo": {"Coordenador": 0.15, "Diretor": 0.25}
        }
        """
        if not self.sti_config or not isinstance(self.sti_config, dict):
            return {}
        if "areas" in self.sti_config and isinstance(self.sti_config["areas"], dict):
            return self.sti_config["areas"]
        return self.sti_config

    # --------------------------------------------------------------------
    # Extrai as faixas de STI (mínimo, máximo, target)
    # --------------------------------------------------------------------
    def _extract_sti_ranges(self):
        """
        Retorna um dicionário com ranges de STI.
        Exemplo esperado no sti_config.json:
        {
            "ranges": {
                "Comercial": {"min": 0.8, "max": 1.2},
                "Corporativo": {"min": 0.9, "max": 1.1}
            }
        }
        """
        if not self.sti_config or not isinstance(self.sti_config, dict):
            return {}
        if "ranges" in self.sti_config and isinstance(self.sti_config["ranges"], dict):
            return self.sti_config["ranges"]
        # Fallback: se não houver ranges definidos, gera padrão
        return {area: {"min": 0.8, "max": 1.2} for area in self._extract_sti_levels().keys()}

    # --------------------------------------------------------------------
    # Fallback sem cache
    # --------------------------------------------------------------------
    def _load(self, filename: str, default=None):
        # Usa caminho absoluto baseado na localização deste arquivo
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "data", filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default or {}


# ------------------------------------------------------------------------
# Instância global — acessível via from src.config import DATA
# ------------------------------------------------------------------------
DATA = DataLoader()

# ------------------------------------------------------------------------
# Tabelas de tetos anuais (compatibilidade com cálculos)
# ------------------------------------------------------------------------
ANNUAL_CAPS = {
    "BR": {"INSS": 908.85 * 13, "FGTS": None},
    "CL": {"AFP": 81.6 * 12, "CES": 122.6 * 12},
    "US": {"FICA_SS": 168600, "FICA_MEDICARE": None},
    "CA": {"CPP": 68500, "EI": 63600},
    "MX": {"IMSS": 25 * 365},
}

