from typing import Any, Optional

# Formato padrão para caixas de número
INPUT_FORMAT = "%.2f"

def fmt_money(value: float, sym: str = "R$") -> str:
    """Formata moeda no padrão brasileiro (ex: R$ 1.234,56)."""
    if value is None: return f"{sym} 0,00"
    try:
        formatted = f"{value:,.2f}"
        return f"{sym} {formatted.replace(',', 'X').replace('.', ',').replace('X', '.')}"
    except (ValueError, TypeError): return f"{sym} 0,00"

def money_or_blank(v: float, sym: str) -> str:
    """Retorna a moeda formatada ou string vazia se o valor for zero."""
    return "" if abs(v) < 1e-9 else fmt_money(v, sym)

def fmt_percent(v: Optional[float]) -> str:
    """Formata decimal para porcentagem (0.2 -> 20.0%)."""
    return f"{v*100:.1f}%" if v is not None else "0.0%"

def fmt_cap(cap_value: Any, country_code: str, sym: str = None) -> str:
    """Formata tetos (caps), lidando com UF do Chile."""
    if cap_value is None: return "—"
    if isinstance(cap_value, (int, float)):
        # Regra específica para UF do Chile
        if country_code == "Chile" and cap_value < 500: 
            return f"{cap_value:.1f} UF"
        return fmt_money(cap_value, sym if sym else "")
    return str(cap_value)
