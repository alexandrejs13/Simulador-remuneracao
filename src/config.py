import os
import json
import streamlit as st


class DataLoader:
    """
    Classe responsável por carregar arquivos de configuração JSON.
    Compatível com Streamlit Cloud e cache seguro.
    """

    def __init__(self):
        # Converte todos os defaults para string antes do cache (evita UnhashableParamError)
        default_i18n = json.dumps({"Português": {"sidebar_title": "Carregando..."}})
        default_empty = "{}"

        # Carregamento dos principais arquivos de configuração
        self.i18n = self._load_json("i18n.json", default_str=default_i18n)
        self.sti_config = self._load_json("sti_config.json", default_str=default_empty)
        self.countries = self._load_json("countries.json", default_str=default_empty)
        self.tables = self._load_json("tables.json", default_str=default_empty)

    # --------------------------------------------------------------------
    # Função de leitura com cache — apenas tipos hasháveis (filename, str)
    # --------------------------------------------------------------------
    @st.cache_data(show_spinner=False)
    def _load_json(_self, filename: str, default_str: str = "{}"):
        """
        Lê o conteúdo JSON de um arquivo dentro do diretório /data.
        Usa cache seguro e trata erros de forma silenciosa.
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
    # Versão sem cache — útil para depuração ou recarregar manualmente
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
# (Opcional) Tabelas de tetos anuais — usadas em cálculos de contribuições
# ------------------------------------------------------------------------
ANNUAL_CAPS = {
    "BR": {  # Brasil
        "INSS": 908.85 * 13,  # teto mensal * 13
        "FGTS": None,
    },
    "CL": {  # Chile
        "AFP": 81.6 * 12,
        "CES": 122.6 * 12,
    },
    "US": {  # Estados Unidos
        "FICA_SS": 168600,
        "FICA_MEDICARE": None,
    },
    "CA": {  # Canadá
        "CPP": 68500,
        "EI": 63600,
    },
    "MX": {  # México
        "IMSS": 25 * 365,  # exemplo: 25 UMAs diárias
    },
}
