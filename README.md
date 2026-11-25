# Simulador de Rescisão CLT
Aplicativo Streamlit para estimar demissão sem justa causa, com regras tributárias de 2026. Não armazena entradas. Não publique valores pessoais no repositório.

## Executar
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
## Publicar
Acesse https://share.streamlit.io/ e selecione o repositório, branch main e app.py. GitHub sozinho não hospeda o servidor Python.

## Premissas
- Contrato CLT padrão mensal, FGTS 8%, dispensa sem justa causa. Último dia efetivamente trabalhado, com projeção do aviso indenizado. No aviso trabalhado, parcela acima de 30 dias estimada como indenizada.
- Férias simples restantes e em dobro informadas separadamente; avos proporcionais calculados automaticamente.
- IRRF/INSS de 2026 separados para salário e 13º. Não cobre múltiplas folhas ou antecipações complexas.
- FGTS anterior só entra no total se já disponível por outro motivo. Base da multa anterior aos depósitos finais; saldo como aproximação se desconhecida. Conferir base oficial e depósitos já recolhidos. Não cobre saldo bloqueado, empréstimos ou regimes especiais.
- Atualizar tabelas anualmente; datas fora de 2026 bloqueadas. Não inclui seguro-desemprego.

## Testes
`python -m unittest -v`

## Fontes
- https://www.gov.br/inss/pt-br/direitos-e-deveres/inscricao-e-contribuicao/tabela-de-contribuicao-mensal/
- https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/tabelas/2026
- https://www.fgts.gov.br/Paginas/subpaginas/saque-dispensa.aspx
- https://www.tst.jus.br/documents/d/guest/irr255-pdf
