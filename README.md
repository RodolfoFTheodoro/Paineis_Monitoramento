# Painel de Monitoramento de Nascimentos - Grande ABC

Painel interativo desenvolvido com Streamlit, Pandas e Plotly para analisar os
registros de nascidos vivos do SINASC de 2026 nos sete municípios do Grande ABC.

## Dados

- `SINASC_2026.csv`: base pública nacional fornecida para o projeto.
- `IBGE_municipios.csv`: base auxiliar de municípios do IBGE.
- Municípios filtrados: Santo André, São Bernardo do Campo, São Caetano do Sul,
  Diadema, Mauá, Ribeirão Pires e Rio Grande da Serra.

Os códigos `CODMUNRES` utilizados são: `354780`, `354870`, `354880`, `351380`,
`352940`, `354330` e `354410`.

## Executar

No Windows, a partir da pasta do projeto:

```bat
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Em seguida, abra o endereço exibido pelo Streamlit no navegador.

## Funcionalidades

- Filtros por município, mês e sexo.
- Indicadores de nascimentos, percentual de cesáreas, peso médio e idade média materna.
- Evolução mensal e distribuição por município e tipo de gravidez.
- Distribuição da duração da gestação e do peso ao nascer.
- Comparação do peso por sexo.
- Distribuição das consultas pré-natais.
- Tipo de parto por faixa etária e escolaridade materna.
- Distribuição por raça/cor.
- Visualização dos registros filtrados.