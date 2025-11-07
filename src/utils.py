from typing import Any, Optional

INPUT_FORMAT = "%.2f"

def fmt_currency(value: float, sym: str = "R$") -> str:
    """Formata moeda no padrão brasileiro (ex: R$ 1.234,56)."""
    if value is None: return f"{sym} 0,00"
    try:
        # Formata com separador de milhar e 2 casas decimais
        formatted = f"{value:,.2f}"
        # Troca , por X (placeholder), . por , (decimal) e X por . (milhar)
        return f"{sym} {formatted.replace(',', 'X').replace('.', ',').replace('X', '.')}"
    except (ValueError, TypeError):
        return f"{sym} 0,00"

def money_or_blank(v: float, sym: str) -> str:
    """Retorna a moeda formatada ou string vazia se o valor for zero."""
    return "" if abs(v) < 1e-9 else fmt_currency(v, sym)

def fmt_percent(v: Optional[float]) -> str:
    """Formata um decimal (0.25) para string de porcentagem (25.0%)."""
    return f"{v*100:.1f}%" if v is not None else "0.0%"

def fmt_cap(cap_value: Any, country_code: str, sym: str = None) -> str:
    """Formata valores de teto (cap), tratando casos especiais como UF (Chile)."""
    if cap_value is None: 
        return "—"
    if isinstance(cap_value, (int, float)):
        if country_code == "Chile" and cap_value < 500: 
            return f"{cap_value:.1f} UF"
        return fmt_currency(cap_value, sym if sym else "")
    return str(cap_value)
