from typing import Dict, Any, List, Tuple
from src.config import DATA, ANNUAL_CAPS

# --- CÁLCULOS BRASIL (REGRA DETALHADA) ---
def _calc_inss_br(salary: float, table: Dict) -> float:
    contrib = 0.0
    prev_limit = 0.0
    for faixa in table.get("faixas", []):
        limit = faixa["ate"]
        rate = faixa["aliquota"]
        if salary > prev_limit:
            base = min(salary, limit) - prev_limit
            contrib += base * rate
            prev_limit = limit
        else:
            break
    # Aplica teto se definido na tabela
    teto = table.get("teto_contribuicao")
    if teto:
        contrib = min(contrib, teto)
    return contrib

def _calc_irrf_br(base_ir: float, dependents: int, table: Dict) -> float:
    deduction_per_dep = table.get("deducao_dependente", 0.0)
    net_base = max(base_ir - (deduction_per_dep * dependents), 0.0)
    
    # Encontra a faixa correta (a tabela deve estar ordenada)
    rate = 0.0
    deduction_fix = 0.0
    for faixa in table.get("faixas", []):
        if net_base <= faixa["ate"]:
            rate = faixa["aliquota"]
            deduction_fix = faixa["deducao"]
            break
    
    irrf = (net_base * rate) - deduction_fix
    return max(irrf, 0.0)

def calculate_br_net(salary: float, dependents: int, other_deductions: float, 
                    bonus_annual: float = 0, incide_medias: bool = False) -> Dict:
    inss = _calc_inss_br(salary, DATA.br_inss)
    irrf = _calc_irrf_br(salary - inss, dependents, DATA.br_irrf)
    
    lines = [("Salário Base", salary, 0.0)]
    
    # Nova feature: Médias sobre Bônus
    medias_prov = 0.0
    if incide_medias and bonus_annual > 0:
        # Fórmula: (BONUS/12) + (BONUS/12) + ((BONUS/12)/3)
        monthly_bonus = bonus_annual / 12.0
        medias_prov = (monthly_bonus * 2) + (monthly_bonus / 3.0)
        lines.append(("Provisão Médias s/ Bônus", medias_prov, 0.0))

    lines.append(("INSS", 0.0, inss))
    lines.append(("IRRF", 0.0, irrf))
    if other_deductions > 0:
        lines.append(("Outras Deduções", 0.0, other_deductions))

    total_earn = salary + medias_prov
    total_ded = inss + irrf + other_deductions
    
    return {
        "lines": lines,
        "total_earnings": total_earn,
        "total_deductions": total_ded,
        "net_salary": total_earn - total_ded,
        "fgts": salary * 0.08 # Informativo
    }

# --- CÁLCULOS EUA ---
def calculate_us_net(salary: float, other_deductions: float, state_rate: float, state_name: str) -> Dict:
    # FICA (Social Security + Medicare)
    ss_cap_monthly = ANNUAL_CAPS["US_FICA"] / 12.0
    ss_tax = min(salary, ss_cap_monthly) * 0.062
    med_tax = salary * 0.0145
    
    state_tax_val = salary * state_rate
    
    lines = [
        ("Base Salary", salary, 0.0),
        ("Social Security (6.2%)", 0.0, ss_tax),
        ("Medicare (1.45%)", 0.0, med_tax)
    ]
    if state_rate > 0:
        lines.append((f"State Tax - {state_name} ({state_rate*100:.2f}%)", 0.0, state_tax_val))
    if other_deductions > 0:
        lines.append(("Other Deductions", 0.0, other_deductions))
        
    total_ded = ss_tax + med_tax + state_tax_val + other_deductions
    return {
        "lines": lines,
        "total_earnings": salary,
        "total_deductions": total_ded,
        "net_salary": salary - total_ded,
        "fgts": 0.0
    }

# --- CÁLCULOS GENÉRICOS (Outros Países) ---
def calculate_generic_net(country: str, salary: float, other_deductions: float) -> Dict:
    # Tenta pegar taxas simplificadas do country_tables.json se existirem
    rates = DATA.country_tables.get("TABLES", {}).get(country, {}).get("rates", {})
    
    lines = [("Salário Base", salary, 0.0)]
    total_ded = 0.0
    
    for tax_name, rate in rates.items():
        # Simplificação: aplica taxa sobre o bruto total (ajustar se necessário regras de teto por país)
        val = salary * rate
        # Exceção rápida para tetos conhecidos se quiser refinar:
        if country == "México" and "IMSS" in tax_name:
             val = min(salary, ANNUAL_CAPS["MX_UMA_MONTHLY"]) * rate

        lines.append((tax_name, 0.0, val))
        total_ded += val

    if other_deductions > 0:
        lines.append(("Outras Deduções", 0.0, other_deductions))
        total_ded += other_deductions

    return {
        "lines": lines,
        "total_earnings": salary,
        "total_deductions": total_ded,
        "net_salary": salary - total_ded,
        "fgts": 0.0
    }

# --- FACHADA PRINCIPAL DE CÁLCULO ---
def get_net_salary(country: str, salary: float, **kwargs) -> Dict:
    if country == "Brasil":
        return calculate_br_net(salary, kwargs.get('dependents',0), kwargs.get('other_deductions',0), 
                                kwargs.get('bonus_annual',0), kwargs.get('incide_medias',False))
    elif country == "Estados Unidos":
        return calculate_us_net(salary, kwargs.get('other_deductions',0), 
                                kwargs.get('state_rate',0), kwargs.get('state_code',''))
    else:
        return calculate_generic_net(country, salary, kwargs.get('other_deductions',0))

# --- CUSTO EMPREGADOR ---
def get_employer_cost(country: str, salary_monthly: float, bonus_annual: float, incide_bonus: bool) -> Dict:
    months_factor = DATA.country_tables["REMUN_MONTHS"].get(country, 12.0)
    charges_list = DATA.country_tables["EMPLOYER_COST"].get(country, [])
    
    annual_base_salary = salary_monthly * 12.0
    # Base anual para encargos que incidem sobre férias/13º (Brasil, etc)
    annual_base_with_benefits = salary_monthly * months_factor 
    
    total_charges = 0.0
    breakdown = []

    for charge in charges_list:
        # Decide qual base usar. EUA/Canadá geralmente aplicam sobre o salário base apenas.
        # Países latinos com 13º/Férias obrigatórios aplicam sobre o montante total.
        if country in ["Estados Unidos", "Canadá"]:
             current_base = annual_base_salary
        else:
             current_base = annual_base_with_benefits
             
        # Adiciona bônus à base se o encargo permite E se a opção foi marcada
        if charge.get("bonus") and incide_bonus:
             current_base += bonus_annual
             
        # Aplica teto anual se existir
        teto = charge.get("teto")
        if teto is not None:
             current_base = min(current_base, float(teto))
             
        val = current_base * (charge["percentual"] / 100.0)
        total_charges += val
        breakdown.append({"Item": charge["nome"], "Valor": val, "Rate": charge["percentual"]})
        
    total_annual_cost = (salary_monthly * months_factor) + bonus_annual + total_charges
    multiplier = (total_annual_cost / annual_base_salary) if annual_base_salary > 0 else 0
    
    return {
        "total_cost": total_annual_cost,
        "total_charges": total_charges,
        "multiplier": multiplier,
        "months_factor": months_factor,
        "breakdown": breakdown
    }

# --- AUXILIARES STI ---
def get_sti_targets(area: str, level: str) -> Tuple[float, float]:
    ranges = DATA.sti_config["STI_RANGES"].get(area, {})
    return ranges.get(level, (0.0, 0.0)) # Retorna tupla (min, max)
