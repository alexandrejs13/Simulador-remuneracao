import os
import json
import streamlit as st


class DataLoader:
    """
    Carrega arquivos JSON e mantém cache seguro.
    Compatível com Streamlit Cloud e Python 3.13.
    """

    def __init__(self):
        # ⚠️ Aqui o default é convertido para JSON string ANTES de ser passado à função cacheada
        default_i18n = json.dumps({"Português": {"sidebar_title": "Carregando..."}})
        self.i18n = self._load_json("i18n.json", default_str=default_i18n)
        self.sti_config = self._load_json("sti_config.json", default_str="{}")
        self.countries = self._load_json("countries.json", default_str="{}")
        self.tables = self._load_json("tables.json", default_str="{}")

    # --------------------------------------------------------------
    # Função cacheada — nunca recebe dicts, apenas strings e nomes
    # --------------------------------------------------------------
    @st.cache_data(show_spinner=False)
    def _load_json(_self, filename: str, default_str: str = "{}"):
        """
        Lê o arquivo JSON em cache seguro.
        """
        try:
            path = os.path.join("data", filename)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            # Se arquivo não existir, retorna o default convertido
            return json.loads(default_str)
        except Exception as e:
            st.warning(f"Erro ao carregar {filename}: {e}")
            try:
                return json.loads(default_str)
            except Exception:
                return {}

    # --------------------------------------------------------------
    # Versão sem cache (para testes ou fallback)
    # --------------------------------------------------------------
    def _load(self, filename: str, default=None):
        path = os.path.join("data", filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default or {}


# Instância global única
DATA = DataLoader()
