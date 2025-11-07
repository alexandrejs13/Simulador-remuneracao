import os
import json
import streamlit as st


class DataLoader:
    """
    Classe central de carregamento de arquivos JSON e parâmetros de configuração
    com cache seguro e compatibilidade total com Streamlit Cloud.
    """

    def __init__(self):
        # Carrega arquivos de configuração no momento da inicialização
        self.i18n = self._load_json(
            "i18n.json",
            default={"Português": {"sidebar_title": "Carregando..."}}
        )
        self.sti_config = self._load_json("sti_config.json", default={})
        self.countries = self._load_json("countries.json", default={})
        self.tables = self._load_json("tables.json", default={})

    # 🔹 Função principal de carregamento com tratamento de erro e fallback
    @st.cache_data(show_spinner=False)
    def _load_json(_self, filename: str, default_str: str = "{}"):
        """
        Lê um arquivo JSON do diretório 'data' com cache seguro.
        Parâmetros complexos (como dict) são convertidos em string JSON para evitar erros de hash.
        """
        try:
            path = os.path.join("data", filename)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)

            # Retorna valor padrão (já convertido em string)
            return json.loads(default_str)
        except Exception as e:
            st.warning(f"Erro ao carregar {filename}: {e}")
            try:
                return json.loads(default_str)
            except Exception:
                return {}

    # 🔹 Função pública de leitura (sem cache)
    def _load(self, filename: str, default=None):
        """
        Carrega um arquivo JSON sem cache (uso eventual, backup).
        """
        path = os.path.join("data", filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default or {}


# ✅ Instância global acessível pelo app
DATA = DataLoader()
