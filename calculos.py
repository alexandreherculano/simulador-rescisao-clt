from datetime import timedelta
from calendar import monthrange
from dateutil.relativedelta import relativedelta

def inss(v):
    return round(sum(max(0,min(v,b)-a)*r for a,b,r in [(0,1621,.075),(1621,2902.84,.09),(2902.84,4354.27,.12),(4354.27,8475.55,.14)]),2)

def irrf(v, previdencia, dependentes=0, pensao=0):
    base=max(0,v-max(607.20,previdencia+189.59*dependentes+pensao))
    for teto,aliq,ded in [(2428.80,0,0),(2826.65,.075,182.16),(3751.05,.15,394.16),(4664.68,.225,675.49),(float('inf'),.275,908.73)]:
        if base<=teto: break
    imposto=max(0,base*aliq-ded)
    reducao=312.89 if v<=5000 else max(0,978.62-.133145*v) if v<=7350 else 0
    return round(max(0,imposto-reducao),2)

def avos_13(admissao, fim, ano):
    from datetime import date
    return sum((min(fim,date(ano,m,monthrange(ano,m)[1]))-max(admissao,date(ano,m,1))).days+1>=15 for m in range(1,13))

def ferias(admissao,fim):
    delta=relativedelta(fim+timedelta(days=1),admissao)
    return delta.years,delta.months+(delta.days>=15)

def fgts_historico(admissao, saida, salario):
    """Depósitos estimados anteriores ao mês da saída e ao 13º rescisório."""
    from datetime import date
    if saida < admissao: raise ValueError('Data de saída anterior à admissão.')
    mes = admissao.replace(day=1)
    limite = saida.replace(day=1)
    total = 0.0
    while mes < limite:
        ultimo = mes.replace(day=monthrange(mes.year, mes.month)[1])
        dias = 30 if admissao <= mes else min(30, (ultimo-admissao).days+1)
        total += salario*dias/30*.08
        mes += relativedelta(months=1)
    for ano in range(admissao.year, saida.year):
        total += salario*avos_13(admissao,date(ano,12,31),ano)/12*.08
    return round(total,2)

def calcular(admissao,saida,salario,aviso,dias_ferias,fgts,base_fgts,modalidade,dependentes=0,adiantamento=0,extras=0,descontos=0,filhos=0,dias_dobro=0,depositos_pendentes=0,ja_depositado=0):
    if saida<admissao: raise ValueError('Data de saída anterior à admissão.')
    anos=relativedelta(saida,admissao).years
    prazo=min(90,30+3*anos)
    dias_aviso=prazo if aviso=='Indenizado' else max(0,prazo-30)
    fim=saida+timedelta(days=dias_aviso)
    if saida.year!=2026 or fim.year!=2026: raise ValueError('Esta versão usa tabelas de 2026 e não cobre projeções para outro ano.')
    dias=min(30,saida.day) if saida.day!=monthrange(saida.year,saida.month)[1] else 30
    if admissao.year==saida.year and admissao.month==saida.month: dias=min(dias,(saida-admissao).days+1)
    saldo=round(salario*dias/30,2)
    _,avos=ferias(admissao,fim)
    anos_real,_=ferias(admissao,saida)
    anos_proj,_=ferias(admissao,fim)
    adquiridas=round(salario*(dias_ferias+30*max(0,anos_proj-anos_real)+2*dias_dobro)/30,2)
    proporcionais=round(salario*avos/12,2)
    terco=round((adquiridas+proporcionais)/3,2)
    decimo=round(salario*avos_13(admissao,fim,saida.year)/12,2)
    decimo_real=round(salario*avos_13(admissao,saida,saida.year)/12,2)
    indenizado=round(salario*dias_aviso/30,2)
    familia=round(67.54*filhos*dias/30,2) if salario+extras<=1980.38 else 0
    p={'Saldo salarial':saldo,'Aviso indenizado':indenizado,'13º salário':decimo,'Férias adquiridas / em dobro':adquiridas,'Férias proporcionais':proporcionais,'1/3 de férias':terco,'Salário-família':familia,'Outros créditos tributáveis':extras}
    i=inss(saldo+extras); i13=inss(decimo)
    d={'INSS salário':i,'INSS 13º':i13,'IRRF salário':irrf(saldo+extras,i,dependentes),'IRRF 13º':irrf(decimo,i13,dependentes),'Adiantamento 13º':adiantamento,'Outros descontos':descontos}
    bruto=round(sum(p.values()),2); liquido=round(bruto-sum(d.values()),2)
    novos=max(0,round(.08*(saldo+extras+decimo+indenizado)+depositos_pendentes-ja_depositado,2))
    # Tema 255 TST: excluir a projeção do aviso da base estimada da multa.
    base_nova=max(0,round(.08*(saldo+extras+decimo_real)+depositos_pendentes-ja_depositado,2))
    multa=round(.4*((fgts if base_fgts is None else base_fgts)+base_nova),2)
    saque=round(fgts+novos,2) if modalidade=='Saque-rescisão' else 0
    return dict(proventos=p,descontos=d,bruto=bruto,liquido=liquido,novos=novos,multa=multa,saque=saque,total=round(liquido+saque+multa,2),retido=round(0 if modalidade=='Saque-rescisão' else fgts+novos,2),fim=fim,avos=avos,prazo=prazo,dias_aviso=dias_aviso)
