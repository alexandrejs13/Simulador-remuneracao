def fmt_currency(value: float, symbol: str = "R$") -> str:
    """Formata moeda no padrão brasileiro (ex: R$ 1.234,56)."""
    if value is None: return f"{symbol} 0,00"
    try:
        formatted = f"{value:,.2f}"
        return f"{symbol} {formatted.replace(',', 'X').replace('.', ',').replace('X', '.')}"
    except:
        return f"{symbol} 0,00"

def fmt_percent(value: float) -> str:
    """Formata decimal para porcentagem (0.2 -> 20.0%)."""
    return f"{value*100:.1f}%" if value is not None else "0.0%"
