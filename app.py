import streamlit as st
from datetime import date
from calculos import calcular
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
    fgts=dinheiro('Saldo atual da conta do empregador atual')
    modalidade=st.radio('Modalidade vigente',['Saque-rescisão','Saque-aniversário'])
    usar_base=st.checkbox('Conheço a base para fins rescisórios')
    base=dinheiro('Base para multa antes dos depósitos finais') if usar_base else None
    if not usar_base: st.caption('A multa será aproximada usando o saldo atual; saques anteriores podem alterar a base real.')
    anteriores=dinheiro('Saldo total de empregos anteriores')
    liberado=dinheiro('Parte dos saldos anteriores já liberada para saque', 'Não inclua valores ainda bloqueados ou sujeitos a condição futura.')
    pendentes=dinheiro('Depósitos anteriores ainda não recolhidos')
    depositado=dinheiro('Depósitos das verbas finais já incluídos no saldo informado','Evita dupla contagem; se a base da multa tiver composição diferente, revise manualmente.')
with st.expander('Adiantamentos e outros ajustes'):
    adiant=dinheiro('13º já recebido (valor bruto adiantado)')
    extras=dinheiro('Outros créditos salariais tributáveis (horas extras etc.)')
    descontos=dinheiro('Outros descontos líquidos / adiantamentos')
if salario<=0: st.info('Informe o salário para calcular.'); st.stop()
if liberado>anteriores: st.error('O saldo anterior liberado não pode superar o saldo anterior total.'); st.stop()
try: r=calcular(adm,saida,salario,aviso,ferias,fgts,base,anteriores,modalidade,liberado,dep,adiant,extras,descontos,filhos,dobro,pendentes,depositado)
except ValueError as e: st.error(str(e)); st.stop()
st.divider()
st.metric('TOTAL LÍQUIDO DISPONÍVEL ESTIMADO',moeda(r['total']))
c=st.columns(4)
for col,label,key in zip(c,['Acerto líquido','Multa de 40%','FGTS atual sacável','FGTS anterior liberado'],['liquido','multa','saque','anterior']): col.metric(label,moeda(r[key]))
st.caption(f"FGTS não disponível: {moeda(r['retido'])} • Depósitos finais estimados: {moeda(r['novos'])} • Aviso indenizado: {r['dias_aviso']} dias • Fim projetado: {r['fim']:%d/%m/%Y}")
with st.expander('Memória de cálculo',expanded=True):
    c,d=st.columns(2)
    with c:
        st.write('**Proventos**'); st.table([{'Verba':k,'Valor':moeda(v)} for k,v in r['proventos'].items()]); st.write('Bruto:',moeda(r['bruto']))
    with d:
        st.write('**Descontos**'); st.table([{'Verba':k,'Valor':moeda(v)} for k,v in r['descontos'].items()])
    import json
    st.download_button('Exportar resultado JSON',json.dumps(r,ensure_ascii=False,indent=2,default=str),file_name='rescisao.json',mime='application/json')
st.warning('Estimativa, não substitui o TRCT. Não cobre bloqueios judiciais/antecipações de FGTS, convenções coletivas, rendimentos anteriores no mesmo mês, ajustes de folha ou projeções para 2027. Não inclui seguro-desemprego. Nenhum dado é gravado pelo aplicativo.')
