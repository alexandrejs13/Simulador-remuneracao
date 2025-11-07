import pandas as pd
from core.formatter import fmt_money
from utils.helpers import calc_inss, calc_irrf, calc_fgts

def calcular_salario_liquido_br(salario, dependentes, outras_deducoes, bonus_anual, incide_fgts, inss_data, irrf_data):
    inss = calc_inss(salario, inss_data)
    base_ir = salario - inss
    irrf = calc_irrf(base_ir, dependentes, irrf_data)
    fgts = calc_fgts(salario, bonus_anual, incide_fgts)

    total_deducoes = inss + irrf + outras_deducoes
    salario_liquido = salario - total_deducoes

    resumo = pd.DataFrame({
        "Descrição": ["Salário Bruto", "INSS", "IRRF", "Outras Deduções", "FGTS", "Salário Líquido"],
        "Valor": [
            fmt_money(salario),
            fmt_money(-inss),
            fmt_money(-irrf),
            fmt_money(-outras_deducoes),
            fmt_money(fgts),
            fmt_money(salario_liquido)
        ]
    })

    return resumo, salario_liquido, fgts
