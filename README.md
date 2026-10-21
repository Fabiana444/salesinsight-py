![Capa do projeto SalesInsight PY](assets/capa-salesinsight.png.png)
*Imagem de capa produzida com inteligência artificial (IA).*

# salesinsight-py
# Análise e Visualização de Dados de Vendas


## Sobre o projeto
Analise e visualizacao de dados de vendas desenvolvida em Python. O projeto carrega, limpa, transforma, agrega e visualiza um dataset de
vendas, gerando metricas por periodo, produto, categoria e regiao, além de uma segmentacao simples de clientes por faixa de gasto.
 
## O que o projeto analisa
- Receita total e volume de vendas por mês e por trimestre
- Top produtos e categorias por receita
- Desempenho por regiao
- Segmentacao de clientes por nível de gasto (Bronze, Prata, Ouro)
- Relação entre quantidade vendida e receita por transação
- Exportação de relatorios em CSV e JSON e de gráficos em PNG
 
## Conceitos aplicados (Modulo 01 - Semanas 01 a 07)
- Logica de programacao: variáveis, tipos, operadores, condicionais
- Estruturas de dados: listas, tuplas, dicionários e compostas
- Funções: parâmetros, retorno, lambda, ordem superior
- Leitura e escrita de arquivos CSV e JSON
- Módulo datetime e conversão de tipos (cast)
- Pandas:DataFrames, filtros, groupby, transformações
- Matplotlib e Seaborn: linha, barra, dispersao, subplots, export
- Git e GitHub: branches, commits e GitFlow simplificado
 
## Como executar
 
### Google Colab (recomendado)
1. Faça upload de salesinsight.py e de vendas.csv para o Colab.
2. Execute: !python salesinsight.py
3. Ou cole o conteúdo em células de um notebook .ipynb
 
### Localmente com VS Code
1. Instale o Python 3.10+ e o VS Code.
2. Instale as dependências:
   pip install pandas numpy matplotlib seaborn
3. Execute no terminal: python salesinsight.py
 
## Estrutura do projeto
salesinsight-py/
|-- salesinsight.py         # fluxo principal
|-- vendas.csv              # dataset (gerado ou externo)
|-- README.md
|-- outputs/
    |-- metricas_por_mes.csv
    |-- segmentacao_clientes.csv
    |-- estatisticas_gerais.json
    |-- graficos/*.png
 
## Decisoes técnicas
Explique aqui, em poucas linhas, ao menos uma escolha que você fez - por exemplo, por que remover os data inválidos em vez de
mantê-los.
 
## Ferramentas utilizadas
- Python 3.10+
- Google Colab / VS Code
- Bibliotecas: pandas, numpy, matplotlib, seaborn, json, datetime, os, random
- GitHub (e GitHub Desktop, opcional) para versionamento
- Trello / GitHub Projects para o Kanban (opcional)
 
## Video de demonstração
[inserir o link do Google Drive ou do YouTube aqui]



### Documento elaborado para o curso Desenvolvimento de IA para Análise Preditiva — Módulo 01, Semana 07.

