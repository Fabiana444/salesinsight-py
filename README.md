![Capa do projeto SalesInsight PY](assets/capa-salesinsight.png.png)
*Imagem de capa produzida com inteligência artificial (IA).*

# SalesInsight PY — Análise e Visualização de Dados de Vendas


## Sobre o projeto
O SalesInsight PY é um projeto de análise e visualização de dados de vendas desenvolvido em Python como mini-projeto avaliativo do curso Desenvolvimento de IA para Análise Preditiva, Módulo 01, do SC TEC - Senai SC.
O projeto realiza o carregamento, a inspeção, a limpeza e a transformação de um conjunto de dados de vendas. Em seguida, calcula métricas, analisa o desempenho comercial, segmenta clientes por faixa de gasto, gera gráficos e exporta os resultados em arquivos CSV e JSON.
O objetivo é organizar um fluxo de análise de dados que carregue, transforme, agregue e visualize um dataset de vendas, gerando insights relevantes e exportando os resultados.
Para alcançá-lo é necessário atender o desafio de gerar um relatório analítico, a partir de um histórico de vendas, que responda as seguintes perguntas:
- Como as vendas se comportam ao longo do tempo (por mês e por trimestre);
- Quais produtos e categorias geram mais receita?
- Quais regiões têm melhor desempenho?
- Quais clientes são mais valiosos (segmentação simples por faixa de gasto)?
- Existe relação entre a quantidade vendida e a receita gerada por transação?


 ## O que o projeto analisa

### Visualizações em PNG para facilitar a interpretação dos resultados
- Receita total por mês.

- Receita total por região.

-Receita por categoria e produto.

- Receita total por mês e categoria.

_ Receita por trimestre e top 5 produtos.

- Receita por segmento de cliente e categoria de produto.

- Quantidade de clientes por região e segmento.

- Quantidade versus receita por categoria.

- Top 5 produtos por receita.

- Vendas por dia da semana.

- Mapa de calor da receita total por produto e categoria.

- Painel resumo.


### Exportação de

- Métricas por mês (csv).

- Segmentação de clientes (CSV).

- Estatísticas gerais em JSON.


 
## Conceitos aplicados (Modulo 01 - Semanas 01 a 07)
O desenvolvimento do projeto aplica conceitos de programação e análise de dados abordados no curso:
- Logica de programacao: variáveis, tipos, operadores, condicionais
- Estruturas de dados: listas, tuplas, dicionários e compostas
- Funções: parâmetros, retorno, lambda, ordem superior
- Leitura e escrita de arquivos CSV e JSON
- Módulo datetime e conversão de tipos (cast)
- Pandas:DataFrames, filtros, groupby, transformações
- Matplotlib e Seaborn: linha, barra, dispersao, subplots, export
- Git e GitHub: branches, commits e GitFlow simplificado

 
 ## Bibliotecas e ferramentas utilizadas

 ### Linguagem e bibliotecas Python
- Python 3.10 ou superior: linguagem utilizada no desenvolvimento.

- Pandas: manipulação, organização, transformação e análise dos dados.

- NumPy: operações numéricas.

- Matplotlib: criação e exportação de gráficos.

- Seaborn: visualizações e análise gráfica.

- json e csv: leitura e escrita de arquivos.

- datetime: tratamento e manipulação de datas.

- os: manipulação de caminhos e diretórios.

- random: geração de dados de exemplo.

Os módulos json, datetime, os e random fazem parte da biblioteca padrão do Python, não sendo necessário instalá-los separadamente.


## Ambiente e ferramentas de desenvolvimento

- Visual Studio Code (VS Code): editor utilizado para desenvolver e executar o projeto localmente.

- Git e GitHub: controle de versão e armazenamento do repositório.

- Google Colab: ambiente para desenvolvimento e testes em notebooks.

- Trello: organização das tarefas e acompanhamento das etapas do projeto.


## Como executar

### Pré-requisitos
Para executar o projeto localmente, é necessário ter:

- Python 3.10 ou superior.

- Git, caso queira clonar o repositório.

- Um terminal ou editor de código, como o VS Code.

- Conexão com a internet para clonar o repositório ou instalar as bibliotecas, quando necessário.

 
### Execução local com VS Code
1. Clone o repositório do GitHub:

git clone https://github.com/Fabiana444/salesinsight-py.git

2. Acesse a pasta do projeto.

cd salesinsight-py

3. Instale as dependências.

No terminal, execute:

python -m pip install pandas numpy matplotlib seaborn

4. Execute o programa.

python salesinsight.py

O programa executará as etapas de carregamento, limpeza, transformação, análise, geração de gráficos, apresentação do resumo e exportação dos resultados.

5. Confira os arquivos gerados.

Após a execução, verifique a pasta outputs, que contém os relatórios e a subpasta graficos, com as visualizações exportadas em PNG.

O arquivo vendas.csv é utilizado como conjunto de dados de entrada. Caso não esteja disponível, o programa possui uma etapa para gerar o conjunto de dados, conforme a implementação do projeto.

 
### Execução no Colab
O projeto também pode ser executado no Google Colab.

1. Abra um notebook no Google Colab.
2. Envie os arquivos salesinsight.py e vendas.csv para o ambiente de execução. Se o arquivo de dados não estiver disponível, o programa poderá gerá-lo conforme sua implementação.

3. Dependências:
O Google Colab já possui Pandas, NumPy, Matplotlib e Seaborn instalados.

4. Execute o programa:

!python salesinsight.py

5. Confira as mensagens de execução e os arquivos gerados na pasta outputs.

Observação: os arquivos criados no ambiente do Colab ficam nesse ambiente de execução. Para mantê-los no computador, será necessário baixá-los ou salvá-los.

 ```
## Estrutura do projeto

salesinsight-py/
├── assets/
│   └── capa-salesinsight.png.png
├── outputs/
│   ├── metricas_por_mes.csv
│   ├── segmentacao_clientes.csv
│   ├── estatisticas_gerais.json
│   └── graficos/
│       ├── mapa_calor_receita_produto_categoria.png
│       ├── painel_resumo.png
│       ├── quantidade_clientes_regiao_segmento.png
│       ├── quantidade_vs_receita.png
│       ├── receita_categoria_produtos.png
│       ├── receita_por_mes.png
│       ├── receita_por_mes_categoria.png
│       ├── receita_por_regiao.png
│       ├── receita_por_trimestre_top5.png
│       ├── receita_segmento_cliente_categoria_produto.png
│       ├── top_produtos.png
│       └── vendas_por_dia_semana.png
├── salesinsight.py          # fluxo principal
├── vendas.csv               # dataset (gerado ou externo)
└── README.md
```


O arquivo salesinsight.py contém as funções de processamento e análise, a classe AnalisadorDeVendas e o ponto de entrada do programa.

O arquivo vendas.csv contém os dados utilizados na análise. A pasta assets armazena a imagem de capa da documentação. A pasta outputs reúne os resultados exportados durante a execução.


## Arquivos gerados

### metricas_por_mes.csv

Arquivo CSV que reúne as métricas mensais de vendas, incluindo:

- mes: número do mês.

- receita_total: receita total do mês.

- quantidade_vendida: quantidade vendida no mês.

- n_vendas: número de vendas contabilizadas no mês.


### segmentacao_clientes.csv
Arquivo CSV que apresenta os clientes segmentados, com as seguintes informações:

- cliente: identificação do cliente.

- total_gasto: gasto total atribuído ao cliente.

- segmento: classificação do cliente nos níveis Bronze, Prata ou Ouro.


### estatisticas_gerais.json
Arquivo JSON que armazena estatísticas gerais calculadas pelo projeto, incluindo receita total, quantidade vendida, total de vendas, ticket médio geral, métricas trimestrais e valores relacionados aos segmentos de clientes e às categorias de produtos.


## Funcionalidades implementadas
O projeto foi organizado em etapas que compõem o fluxo de análise de dados:

1. Geração e carregamento dos dados: Geração do dataset sinteticamente no próprio código (recomendado, pois garante a reprodução por qualquer pessoa).

2. Inspeção dos dados: verificação das informações, dimensões, tipos de dados e valores ausentes.

3. Limpeza dos dados: conversão e validação das datas de venda e remoção dos registros com datas inválidas. Foram executadas a remoção de espaços extras em colunas de texto; conversão de data com datetime; manutenção de int para quantidade e float para preco_unitario; e gerado relatório de limpeza.

4. Transformação dos dados: Antes de executar esta etapa foi gerada uma cópia do Dataframe original tratado com df_rf04 = df_limpo.copy(). A ação busca preservar o Dataframe tratado.
A seguir, foram criadas colunas derivadas, como receita total, mês, nome do mês, trimestre, ano e faixa de receita por item.

5. Análise das vendas: cálculo de métricas por período, produto, categoria e região:
- Receita total, quantidade vendida e número de vendas por mês;
- Receita total por produto (Top 5, em ordem decrescente);
- Receita total por categoria;
- Receita total e ticket médio por região.
- Todas as demais já citadas em "O que o projeto analisa" (visualizações).

6. Segmentação de clientes: classificação dos clientes de acordo com os níveis de gasto.

| Gasto total acumulado | Segmento |
|---|---|
| Abaixo de R$ 5.000,00 | Bronze |
| De R$ 5.000,00 a R$ 15.000,00 | Prata |
| Acima de R$ 15.000,00 | Ouro |

7. Funções reutilizáveis e função de ordem superior: aplicação de função para processar colunas e demonstrar o conceito de função de ordem superior.

8. Visualização dos dados: geração de gráficos para representar os resultados das análises.

9. Exportação dos resultados: gravação das métricas e estatísticas em arquivos CSV e JSON.

10. Execução completa do fluxo (ponto de entrada): utilização da classe AnalisadorDeVendas para organizar as etapas e executar o processamento completo por meio do ponto de entrada main().


## Decisões técnicas
Durante o processamento, foram adotadas decisões para manter a consistência dos dados e organizar as etapas de análise. Entre elas:

Tratamento de datas inválidas: foram identificados seis registros com datas inválidas, que foram removidos antes das análises temporais. Essa decisão evita que registros sem datas válidas comprometam os agrupamentos por mês, trimestre e ano.

Geração de cópia do Dataframe bruto: Após o tratamento do Dataframe bruto foi adotada a medida de gerar uma cópia antes da criação de colunas derivadas, preservando o Dataframe original tratado para possíveis análises posteriores.

Padronização dos gráficos: Toda as figuras exportadas seguem um padrão global. O uso de uma mesma paleta de cores e de tamnho assegura consistência visual e melhora a experiência de usuários.

O programa utiliza:
### Configuração visual global
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["axes.titlesize"] = 14

Geração de atividades Bônus e gráficos extras: Optou-se por analisar dados e gerar gráficos extras (que não constam como pré-requisitos da avaliação). A decisão decorre de existirem dados relevantes que podem constribuir para o resulado final da análise.
Também foram executadas tarefas bônus que contribuem tanto para a análise dos dados como para o enriquecimento de conhecimento acadêmico.

Organização do fluxo de execução: A classe AnalisadorDeVendas foi criada para reunir as etapas do processamento em uma sequência organizada, reutilizando as funções desenvolvidas anteriormente. O método executar() coordena as etapas e o ponto de entrada main() permite iniciar o programa.
 

## Respostas às perguntas do desafio

1. Como as vendas se comportam ao longo do tempo?
<p>Por mês: fevereiro teve a maior receita, com R$ 186.065,22, seguido de outubro, com R$ 181.878,41. Setembro apresentou a menor receita, com R$ 57.509,42. O comportamento foi irregular ao longo do ano, com aumentos e quedas entre os meses.</p>

<p>Por trimestre: o primeiro trimestre teve 52 vendas, o segundo 42, o terceiro 52 e o quarto 48. Em receita média por venda, o primeiro trimestre apresentou R$ 8.402,14, o segundo R$ 5.807,51, o terceiro R$ 6.596,33 e o quarto R$ 7.424,46.</p>

<p>O primeiro trimestre teve o maior ticket médio, enquanto o segundo teve o menor. A contagem de vendas por trimestre, sozinha, não indica a receita total de cada trimestre; os valores acima são tickets médios, conforme o relatório.</p>

2. Quais produtos e categorias geram mais receita?
<p>Produtos: o Notebook lidera com R$ 493.242,63, seguido de Smartphone, com R$ 343.721,95, e Tablet, com R$ 236.519,71
Categorias: Computadores gera a maior receita, seguido de Celulares e Periféricos.</p>

3. Quais regiões têm melhor desempenho?
<p>A região Centro-Oeste apresenta a maior receita total, enquanto o Nordeste apresenta o maior ticket médio por venda.
Centro-Oeste lidera em faturamento total; Nordeste lidera em valor médio por venda. A região Sul apresenta a menor receita total e o menor ticket médio.
</p>

4. Quais clientes são mais valiosos?
<p>A segmentação identificou 49 clientes: 35 no segmento Ouro, 9 no Prata e 5 no Bronze.</p>
<p>O cliente de maior gasto foi Cliente_049, com R$ 86.381,62, classificado no segmento Ouro. Em seguida aparecem Cliente_006, com R$ 78.524,09, e Cliente_009, com R$ 72.517,27.</p>
<p>Os clientes Ouro são os mais valiosos em termos de gasto médio, e Cliente_049 é o cliente com maior gasto total identificado na execução.</p>

5. Existe relação entre quantidade vendida e receita por transação?
<p>Sim, existe uma relação direta, mas a quantidade não explica a receita sozinha. A receita de uma venda depende da quantidade vendida multiplicada pelo preço unitário.</p>

<p>Os resultados de teste da função mostram, por exemplo, uma venda com quantidade 9 e receita de R$ 20.405,97, enquanto outra com quantidade 7 apresenta receita de R$ 799,75. Isso evidencia que o preço unitário também influencia o resultado.</p>
<p>Conclusão: vender mais unidades tende a aumentar a receita quando o preço unitário é mantido, mas transações com quantidades semelhantes podem gerar receitas muito diferentes devido aos preços dos produtos.</p>


## Referências da entrega
 
| O quê | Link |
|---|---|
| Kanban do projeto no Trello | <a href="https://trello.com/invite/b/6aa1962934ea1d01a91c6103/ATTI0565e49f5707a3602c5333576834be794277DB95/fabiana-nonjah-kanabanmini-projetosalesinsight-py" target="_blank" rel="noopener noreferrer">Abrir o Kanban no Trello</a> |
| Notebook de testes no Colab | <a href="https://drive.google.com/drive/folders/1RdtG6wAA1oJAwWvBoJStMjP_lVj1h6V2?usp=sharing" target="_blank" rel="noopener noreferrer">Abrir o notebook no Colab</a> |
| Vídeo de demonstração (até 5 minutos) | <a href="COLE_AQUI_O_LINK_DO_VIDEO" target="_blank" rel="noopener noreferrer">Assistir ao vídeo</a> |


## Limitações do projeto
O SalesInsight PY foi desenvolvido como um mini-projeto avaliativo de análise e visualização de dados. As conclusões dependem dos dados utilizados e das métricas calculadas durante a execução.

Os resultados apresentados são descritivos: o projeto organiza e resume os dados disponíveis, mas não deve ser interpretado como um modelo de previsão de vendas.


## Sobre o trabalho

### Documento elaborado para o curso Desenvolvimento de IA para Análise Preditiva — Módulo 01, Semana 07, como parte do mini-projeto avaliativo.

