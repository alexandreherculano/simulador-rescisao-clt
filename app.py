import streamlit as st
from datetime import date
from calculos import calcular, fgts_historico
st.set_page_config(page_title='Simulador de Rescisão CLT',page_icon='💰',layout='wide')
st.title('Simulador de Rescisão CLT')
st.caption('Demissão sem justa causa • estimativa de caixa disponível • tabelas 2026')
def moeda(v): return f'R$ {v:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
def dinheiro(label,help=None): return st.number_input(label,min_value=0.0,step=100.0,format='%.2f',help=help)
a,b=st.columns(2)
with a:
    st.subheader('Contrato de trabalho')
    adm=st.date_input('Admissão',value=date(2025,1,1),min_value=date(1950,1,1),format='DD/MM/YYYY')
    saida=st.date_input('Último dia efetivamente trabalhado',value=date(2026,11,25),format='DD/MM/YYYY')
    salario=dinheiro('Salário bruto mensal')
    aviso=st.radio('Aviso prévio',['Indenizado','Trabalhado'],help='Se trabalhado, informe o último dia de trabalho; dias proporcionais além de 30 são estimados como indenizados.')
    ferias=st.number_input('Dias de férias adquiridas simples ainda não gozadas',min_value=0,max_value=365,value=0)
    dobro=st.number_input('Dias de férias devidos em dobro (não incluídos acima)',min_value=0,max_value=365,value=0)
    filhos=st.number_input('Filhos elegíveis ao salário-família',min_value=0,value=0)
    dep=st.number_input('Dependentes para IRRF',min_value=0,value=0)
with b:
    st.subheader('FGTS')
    metodo=st.radio('Como calcular o FGTS do vínculo atual?',['Estimativa pela admissão e demissão','Informar saldo real'])
    automatico=metodo.startswith('Estimativa')
    fgts=0.0 if automatico else dinheiro('Saldo real do vínculo atual antes dos depósitos finais')
    if automatico:
        st.caption('Estimativa de 8% sobre salários e 13º de anos anteriores, usando o salário informado durante todo o vínculo. Não inclui correção monetária, férias gozadas e seu terço, variações salariais ou saques.')
    modalidade=st.radio('Modalidade vigente',['Saque-rescisão','Saque-aniversário'])
    usar_base=not automatico and st.checkbox('Conheço a base para fins rescisórios')
    base=dinheiro('Base para multa antes dos depósitos finais') if usar_base else None
    if not usar_base and not automatico: st.caption('A multa será aproximada usando o saldo atual; saques anteriores podem alterar a base real.')
    pendentes=0.0 if automatico else dinheiro('Depósitos anteriores ainda não recolhidos')
    depositado=0.0 if automatico else dinheiro('Depósitos das verbas finais já incluídos no saldo informado','Evita dupla contagem; se a base da multa tiver composição diferente, revise manualmente.')
with st.expander('Adiantamentos e outros ajustes'):
    adiant=dinheiro('13º já recebido (valor bruto adiantado)')
    extras=dinheiro('Outros créditos salariais tributáveis (horas extras etc.)')
    descontos=dinheiro('Outros descontos líquidos / adiantamentos')
if salario<=0: st.info('Informe o salário para calcular.'); st.stop()
try:
    if automatico: fgts=fgts_historico(adm,saida,salario)
    r=calcular(adm,saida,salario,aviso,ferias,fgts,base,modalidade,dep,adiant,extras,descontos,filhos,dobro,pendentes,depositado)
except ValueError as e: st.error(str(e)); st.stop()
st.divider()
st.metric('TOTAL LÍQUIDO DISPONÍVEL ESTIMADO',moeda(r['total']))
c=st.columns(3)
for col,label,key in zip(c,['Acerto líquido','Multa de 40%','FGTS do vínculo atual sacável'],['liquido','multa','saque']): col.metric(label,moeda(r[key]))
st.caption(f"FGTS anterior aos depósitos finais: {moeda(fgts)} • FGTS não disponível: {moeda(r['retido'])} • Depósitos finais estimados: {moeda(r['novos'])} • Aviso indenizado: {r['dias_aviso']} dias • Fim projetado: {r['fim']:%d/%m/%Y}")
with st.expander('Memória de cálculo',expanded=True):
    c,d=st.columns(2)
    with c:
        st.write('**Proventos**'); st.table([{'Verba':k,'Valor':moeda(v)} for k,v in r['proventos'].items()]); st.write('Bruto:',moeda(r['bruto']))
    with d:
        st.write('**Descontos**'); st.table([{'Verba':k,'Valor':moeda(v)} for k,v in r['descontos'].items()])
    import json
    st.download_button('Exportar resultado JSON',json.dumps(r,ensure_ascii=False,indent=2,default=str),file_name='rescisao.json',mime='application/json')
st.warning('Estimativa, não substitui o TRCT. Não cobre bloqueios judiciais/antecipações de FGTS, convenções coletivas, rendimentos anteriores no mesmo mês, ajustes de folha ou projeções para 2027. Não inclui seguro-desemprego. Nenhum dado é gravado pelo aplicativo.')
