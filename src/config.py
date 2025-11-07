import os
import json
import streamlit as st


class DataLoader:
    """
    Classe responsável por carregar arquivos JSON e parâmetros do app.
    Compatível com Streamlit Cloud e Python 3.13.
    """

    def __init__(self):
        # Converte os defaults em strings JSON (evita erros de cache)
        default_i18n = json.dumps({"Português": {"sidebar_title": "Carregando..."}})
        default_empty = "{}"

        # Carrega dados
        self.i18n = self._load_json("i18n.json", default_str=default_i18n)
        self.sti_config = self._load_json("sti_config.json", default_str=default_empty)
        self.countries = self._load_json("countries.json", default_str=default_empty)
        self.tables = self._load_json("tables.json", default_str=default_empty)

        # Define atributo auxiliar compatível com versões anteriores
        self.STI_LEVEL_OPTIONS = self._extract_sti_levels()

    # --------------------------------------------------------------------
    # Função cacheada — apenas tipos hasháveis
    # --------------------------------------------------------------------
    @st.cache_data(show_spinner=False)
    def _load_json(_self, filename: str, default_str: str = "{}"):
        """
        Lê um arquivo JSON em cache seguro, compatível com Streamlit Cloud.
        """
        try:
            path = os.path.join("data", filename)
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
    # Cria atributo STI_LEVEL_OPTIONS dinamicamente
    # --------------------------------------------------------------------
    def _extract_sti_levels(self):
        """
        Extrai o dicionário de níveis e áreas de STI a partir do sti_config.json.
        Exemplo esperado de estrutura:
        {
            "Comercial": {"Analista": 0.10, "Gerente": 0.20},
            "Corporativo": {"Coordenador": 0.15, "Diretor": 0.25}
        }
        """
        if not self.sti_config or not isinstance(self.sti_config, dict):
            return {}

        # Se existir chave 'areas' dentro do JSON, prioriza
        if "areas" in self.sti_config and isinstance(self.sti_config["areas"], dict):
            return self.sti_config["areas"]

        # Caso contrário, retorna todo o JSON (compatibilidade antiga)
        return self.sti_config

    # --------------------------------------------------------------------
    # Fallback sem cache
    # --------------------------------------------------------------------
    def _load(self, filename: str, default=None):
        path = os.path.join("data", filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default or {}


# ------------------------------------------------------------------------
# Instância global — acessível via `from src.config import DATA`
# ------------------------------------------------------------------------
DATA = DataLoader()


# ------------------------------------------------------------------------
# Tetos anuais (para cálculos de contribuições)
# ------------------------------------------------------------------------
ANNUAL_CAPS = {
    "BR": {"INSS": 908.85 * 13, "FGTS": None},
    "CL": {"AFP": 81.6 * 12, "CES": 122.6 * 12},
    "US": {"FICA_SS": 168600, "FICA_MEDICARE": None},
    "CA": {"CPP": 68500, "EI": 63600},
    "MX": {"IMSS": 25 * 365},
}
