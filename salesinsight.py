import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


def gerar_dataset_vendas(n_registros=200, seed=42):
	"""Gera um dataset sintético de vendas com dados sujos."""
	random.seed(seed)
	np.random.seed(seed)

	produtos = [
		"Notebook",
		"Smartphone",
		"Tablet",
		"Monitor",
		"Teclado",
		"Mouse",
		"Headset",
	]
	categorias = {
		"Notebook": "Computadores",
		"Smartphone": "Celulares",
		"Tablet": "Celulares",
		"Monitor": "Computadores",
		"Teclado": "Perifericos",
		"Mouse": "Perifericos",
		"Headset": "Perifericos",
	}
	precos = {
		"Notebook": 3500,
		"Smartphone": 2200,
		"Tablet": 1800,
		"Monitor": 1200,
		"Teclado": 250,
		"Mouse": 120,
		"Headset": 350,
	}
	regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
	data_inicio = datetime(2025, 1, 1)
	dados = []

	for i in range(n_registros):
		produto = random.choice(produtos)
		categoria = categorias[produto]
		quantidade = random.randint(1, 10)
		preco = round(precos[produto] * random.uniform(0.85, 1.15), 2)
		data = data_inicio + timedelta(days=random.randint(0, 364))
		data_txt = data.strftime("%Y-%m-%d")
		cliente = f"Cliente_{random.randint(1, 50):03d}"

		# Sujeira proposital para a etapa de limpeza.
		if random.random() < 0.03:
			data_txt = "DATA INVALIDA"

		dados.append(
			{
				"id_venda": i + 1,
				"data_venda": data_txt,
				"cliente": cliente,
				"produto": produto,
				"categoria": categoria,
				"regiao": random.choice(regioes),
				"quantidade": quantidade,
				"preco_unitario": preco,
			}
		)

	return pd.DataFrame(dados)


# Gerar e salvar o CSV bruto.
df_bruto = gerar_dataset_vendas()
df_bruto.to_csv("vendas.csv", index=False)

print(f"Dataset gerado com {len(df_bruto)} registros.")
print(df_bruto.head())


def inspecionar_dados(df):
    """Exibe as informacoes estruturais do DataFrame."""
    print("\n=== INSPECAO INICIAL DO DATASET ===")
    print(f"Shape: {df.shape}")
    print(f"\nColunas: {list(df.columns)}")
    print(f"\nTipos de dados:\n{df.dtypes}")
    print(f"\nValores nulos por coluna:\n{df.isnull().sum()}")
    print(f"\nPrimeiros registros:\n{df.head()}")
    return df
inspecionar_dados(df_bruto)


# RF03 - Tratar os dados (datetime)

def tratar_dados(df):
    """
    Trata o DataFrame de vendas.

    Retorna:
        (df_limpo, relatorio), onde relatorio é um dicionário
        com as contagens de registros iniciais, convertidos e finais.
    """

    # Gerar e usar uma cópia para preservar o DataFrame original
    df_limpo = df.copy()
    registros_iniciais = len(df_limpo)
    tipos_originais = df.dtypes.copy()

    # 1. Remover espaços extras nas colunas de texto
    colunas_texto = ["cliente", "produto", "categoria", "regiao"]
    textos_alterados = pd.Series(False, index=df.index)

    for coluna in colunas_texto:
        texto_original = df[coluna]
        texto_limpo = df_limpo[coluna].str.strip()

        diferencas = (
            texto_original.ne(texto_limpo)
            & ~(texto_original.isna() & texto_limpo.isna())
        ).fillna(False)

        textos_alterados |= diferencas
        df_limpo[coluna] = texto_limpo

    registros_com_texto_alterado = int(textos_alterados.sum())

    # 2. Converter as datas e remover as inválidas
    datas_convertidas = pd.to_datetime(
        df_limpo["data_venda"], errors="coerce"
    )

    datas_validas = int(datas_convertidas.notna().sum())
    datas_invalidas = int(datas_convertidas.isna().sum())

    df_limpo["data_venda"] = datas_convertidas
    df_limpo = df_limpo.dropna(subset=["data_venda"])

    # 3. Ajustar os tipos numéricos
    df_limpo["quantidade"] = df_limpo["quantidade"].astype(int)
    df_limpo["preco_unitario"] = (
        df_limpo["preco_unitario"].astype(float)
    )

    # Contar conversões de tipo por motivo
    conversao_data = (
        datas_validas
        if tipos_originais["data_venda"] != df_limpo["data_venda"].dtype
        else 0
    )

    conversao_quantidade = (
        len(df_limpo)
        if tipos_originais["quantidade"] != df_limpo["quantidade"].dtype
        else 0
    )

    conversao_preco = (
        len(df_limpo)
        if tipos_originais["preco_unitario"]
        != df_limpo["preco_unitario"].dtype
        else 0
    )

    # Identificar registros finais que sofreram alguma alteração
    registros_alterados = pd.Series(False, index=df_limpo.index)

    # A conversão de texto para datetime altera o tipo das datas válidas
    if tipos_originais["data_venda"] != df_limpo["data_venda"].dtype:
        registros_alterados[:] = True

    # Considerar alterações de texto
    registros_alterados |= textos_alterados.loc[df_limpo.index]

    # Considerar alterações de tipo ou de valor nas colunas numéricas
    for coluna in ["quantidade", "preco_unitario"]:
        if tipos_originais[coluna] != df_limpo[coluna].dtype:
            registros_alterados[:] = True
        else:
            diferencas = (
                df.loc[df_limpo.index, coluna]
                .ne(df_limpo[coluna])
                .fillna(False)
            )
            registros_alterados |= diferencas

    registros_convertidos_de_tipo = int(registros_alterados.sum())
    registros_sem_alteracao = int((~registros_alterados).sum())

    # 4. Montar o relatório de limpeza
    registros_finais = len(df_limpo)
    registros_removidos = registros_iniciais - registros_finais

    relatorio = {
        "registros_iniciais": registros_iniciais,
        "datas_validas_convertidas": conversao_data,
        "datas_invalidas": datas_invalidas,
        "quantidade_convertida": conversao_quantidade,
        "preco_unitario_convertido": conversao_preco,
        "registros_com_texto_alterado": registros_com_texto_alterado,
        "registros_convertidos_de_tipo": registros_convertidos_de_tipo,
        "registros_sem_alteracao": registros_sem_alteracao,
        "registros_removidos": registros_removidos,
        "registros_finais": registros_finais,
    }

    print("\n=== RELATÓRIO DE LIMPEZA — RF03 ===")
    print("Registros iniciais:", registros_iniciais)

    print("\nConversões por motivo:")
    print("Datas válidas convertidas para datetime:", conversao_data)
    print("Registros convertidos para quantidade int:", conversao_quantidade)
    print("Registros convertidos para preço float:", conversao_preco)
    print("Registros com texto alterado:", registros_com_texto_alterado)

    print("\nResultado da limpeza:")
    print("Registros convertidos de tipo:", registros_convertidos_de_tipo)
    print("Registros sem alteração:", registros_sem_alteracao)
    print("Datas inválidas encontradas:", datas_invalidas)
    print("Registros removidos:", registros_removidos)
    print("Registros finais:", registros_finais)

    return df_limpo, relatorio


# Executar o RF03
df_limpo, relatorio = tratar_dados(df_bruto)


# RF04 - Criar Colunas Derivadas com Transformações Condicionais

# Criar uma cópia do DataFrame limpo para trabalhar no RF04
df_rf04 = df_limpo.copy()

# Reiniciar os índices após a remoção de linhas no RF03
df_rf04 = df_rf04.reset_index(drop=True)

# 1. Criar a coluna receita_total por operação vetorizada
df_rf04["receita_total"] = (df_rf04["quantidade"] * df_rf04["preco_unitario"])

# 2. Criar a coluna mes(nº mes) extraído da data com .dt.month
df_rf04["mes"] = df_rf04["data_venda"].dt.month

# 3. Criar a coluna nome do mes em portugues com um dicionário de mapeamento
meses = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

df_rf04["mes_nome"] = df_rf04["mes"].map(meses)

# 4. Criar a coluna trimestre no formato Q1 a Q4, a partir de .dt.quarter
df_rf04["trimestre"] = ("Q" + df_rf04["data_venda"].dt.quarter.astype(str))

# 5. Criar a coluna ano extraído da data com .dt.year
df_rf04["ano"] = df_rf04["data_venda"].dt.year

# 6. Criar a coluna faixa_receita_item com classificação condicional
condicoes = [
    df_rf04["receita_total"] < 500,
    ((df_rf04["receita_total"] >= 500) & (df_rf04["receita_total"] < 5000)),
    df_rf04["receita_total"] >= 5000,
]

faixas = ["Baixo Valor", "Medio Valor", "Alto Valor"]

df_rf04["faixa_receita_item"] = "Nao Classificado"

for condicao, faixa in zip(condicoes, faixas):
    df_rf04.loc[condicao, "faixa_receita_item"] = faixa

# Organizar as colunas: dados originais e colunas derivadas
colunas_rf04 = [
    "id_venda",
    "data_venda",
    "cliente",
    "produto",
    "categoria",
    "regiao",
    "quantidade",
    "preco_unitario",
    "receita_total",
    "mes",
    "mes_nome",
    "trimestre",
    "ano",
    "faixa_receita_item",
]

df_rf04 = df_rf04[colunas_rf04]

# Exibir os resultados do RF04
print("\n=== RF04 - COLUNAS DERIVADAS ===")
print("Dimensões:", df_rf04.shape)
print("\nColunas:", list(df_rf04.columns))
print("\nPrimeiros registros:")
print(df_rf04.head().assign(data_venda=df_rf04["data_venda"].head().dt.strftime("%d-%m-%Y")))

print("\nDistribuição das faixas de receita:")
print(df_rf04["faixa_receita_item"].value_counts())

print("\nValores ausentes nas colunas derivadas:")
print(
    df_rf04[
        [
            "receita_total",
            "mes",
            "mes_nome",
            "trimestre",
            "ano",
            "faixa_receita_item",
        ]
    ].isnull().sum()
)


# ============================================================
# B03 - Tabela cruzada mês x categoria
# ============================================================

# Agrupar a receita total por mês e categoria
receita_mes_categoria = df_rf04.groupby(["mes", "mes_nome", "categoria"])["receita_total"].sum().reset_index()

# Criar a tabela cruzada
tabela_mes_categoria = receita_mes_categoria.pivot(
    index=["mes", "mes_nome"],
    columns="categoria",
    values="receita_total"
)

# Exibir a tabela cruzada
print("\n=== B03 - RECEITA TOTAL POR MÊS E CATEGORIA ===")
print(tabela_mes_categoria)


# ============================================================
# RF05 - Calcular métricas agregadas com groupby
# ============================================================

def calcular_metricas(df):
    """
    Calcula as metricas agregadas do dataset.
    Retorna um dicionario no formato {nome_da_metrica: DataFrame}.
    Chaves minimas: por_mes, top_produtos, por_categoria, por_regiao.
    """
    metricas = {}

    # Calcular as metricas por mes
    por_mes = df.groupby("mes").agg({
        "receita_total": "sum",
        "quantidade": "sum",
        "id_venda": "count"
    }).reset_index()

    por_mes = por_mes.rename(columns={
        "quantidade": "quantidade_vendida",
        "id_venda": "n_vendas"
    })

    # Calcular o Top 5 produtos
    top_produtos = df.groupby("produto")["receita_total"].sum().reset_index()
    top_produtos = top_produtos.sort_values("receita_total", ascending=False).head(5)

    # Calcular as metricas por categoria
    por_categoria = df.groupby("categoria")["receita_total"].sum().reset_index()
    por_categoria = por_categoria.sort_values("receita_total", ascending=False)

    # Calcular as metricas por regiao
    por_regiao = df.groupby("regiao")["receita_total"].agg(["sum", "mean"]).reset_index()
    por_regiao = por_regiao.rename(columns={
        "sum": "receita_total",
        "mean": "ticket_medio"
    })
    por_regiao = por_regiao.sort_values("receita_total", ascending=False)

    metricas["por_mes"] = por_mes
    metricas["top_produtos"] = top_produtos
    metricas["por_categoria"] = por_categoria
    metricas["por_regiao"] = por_regiao

    return metricas


# Chamar a função e guardar os resultados
metricas = calcular_metricas(df_rf04)


# Exibir os resultados de Métricas Agregadas com groupby
print("\n=== MÉTRICAS POR MÊS ===")
print(metricas["por_mes"].to_string(index=False, formatters={
    "receita_total": lambda valor: f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
}))

print("\n=== TOP 5 PRODUTOS ===")
print(metricas["top_produtos"].to_string(index=False, formatters={
    "receita_total": lambda valor: f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
}))

print("\n=== MÉTRICAS POR CATEGORIA ===")
print(metricas["por_categoria"].to_string(index=False, formatters={
    "receita_total": lambda valor: f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
}))

print("\n=== MÉTRICAS POR REGIÃO ===")
print(metricas["por_regiao"].to_string(index=False, formatters={
    "receita_total": lambda valor: f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    "ticket_medio": lambda valor: f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
}))


# ============================================================
# EXTRA 2 - ANALISAR VENDAS POR DIA DA SEMANA
# ============================================================

# Criar uma cópia do DataFrame do RF04
df_extra2 = df_rf04.copy()

# Criar a coluna com o nome do dia da semana
dias_semana = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo"
}

df_extra2["dia_semana"] = df_extra2["data_venda"].dt.dayofweek.map(dias_semana)

# Identificar vendas realizadas no fim de semana
df_extra2["fim_de_semana"] = df_extra2["data_venda"].dt.dayofweek >= 5

# Ordenar as vendas da data mais recente para a mais antiga
df_extra2 = df_extra2.sort_values("data_venda", ascending=False)

# Exibir as novas colunas
print("\n\n=== DIAS DA SEMANA E FIM DE SEMANA ===")
print(
    df_extra2[["data_venda", "dia_semana", "fim_de_semana"]]
    .head(10)
    .to_string(
        index=False,
        formatters={
            "data_venda": lambda data: data.strftime("%d-%m-%Y")
        }
    )
)

# Conferir os tipos de dados
print("\n=== TIPOS DE DADOS DAS NOVAS COLUNAS ===")
print(df_extra2[["dia_semana", "fim_de_semana"]].dtypes)

# Definir a ordem dos dias da semana para a análise
ordem_dias = [
    "Domingo",
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado"
]

# Calcular a quantidade de vendas por dia da semana
vendas_por_dia = (
    df_extra2.groupby("dia_semana")
    .size()
    .reindex(ordem_dias, fill_value=0)
    .rename_axis("dia_semana")
    .reset_index(name="quantidade_vendas")
)

# Identificar os dias com maior e menor fluxo de vendas
maior_fluxo = vendas_por_dia["quantidade_vendas"].max()
menor_fluxo = vendas_por_dia["quantidade_vendas"].min()

# Exibir a quantidade de vendas por dia da semana
print("\n=== QUANTIDADE DE VENDAS POR DIA DA SEMANA ===")
print(vendas_por_dia.to_string(index=False))

# Exibir os dias com maior fluxo de vendas
print("\n=== DIAS COM MAIOR FLUXO DE VENDAS ===")
print(
    vendas_por_dia[
        vendas_por_dia["quantidade_vendas"] == maior_fluxo
    ].to_string(index=False)
)

# Exibir os dias com menor fluxo de vendas
print("\n=== DIAS COM MENOR FLUXO DE VENDAS ===")
print(
    vendas_por_dia[
        vendas_por_dia["quantidade_vendas"] == menor_fluxo
    ].to_string(index=False)
)


# ============================================================
# RF06 - SEGMENTAR CLIENTES POR NÍVEL DE GASTO
# ============================================================

def segmentar_clientes(df):
    """
    Agrupa por cliente, soma a receita e classifica em
    Bronze / Prata / Ouro.
    Retorna um DataFrame com: cliente, total_gasto, segmento.
    """
    clientes = df.groupby("cliente")["receita_total"].sum().reset_index()
    clientes = clientes.rename(columns={"receita_total": "total_gasto"})

    clientes["segmento"] = clientes["total_gasto"].apply(
        lambda gasto: "Bronze" if gasto < 5000
        else "Prata" if gasto <= 15000
        else "Ouro"
    )

    return clientes


# Segmentar clientes
clientes_segmentados = segmentar_clientes(df_rf04)

# Exibir os 10 maiores clientes
print("\n\n=== RF06 - 10 MAIORES CLIENTES ===")
print(
    clientes_segmentados
    .sort_values("total_gasto", ascending=False)
    .head(10)
    .to_string(index=False)
)

# Exibir a distribuição de clientes por segmento
print("\n=== RF06 - DISTRIBUIÇÃO DE CLIENTES POR SEGMENTO ===")
print(clientes_segmentados["segmento"].value_counts())


# ============================================================
# RF07 - CRIAR VISUALIZAÇÕES COM MATPLOTLIB
# ============================================================

# ============================================================
# --- Figura 1: Receita total por mês ao longo do período ---
# ============================================================

import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import os
from IPython.display import display, Image

# Configuração visual global
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["axes.titlesize"] = 14

# Criar a pasta para salvar os gráficos
os.makedirs("outputs/graficos", exist_ok=True)

# --- Figura 1: Receita total por mês ---
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(metricas["por_mes"]["mes"], metricas["por_mes"]["receita_total"], marker="o", markersize=7, linewidth=2.5, color="tab:pink", markerfacecolor="tab:cyan", markeredgecolor="white", label="Receita total")
ax.set_title("Receita Total por Mês")
ax.set_xlabel("Mês")
ax.set_ylabel("Receita Total (R$)")
ax.legend()
plt.tight_layout()
plt.savefig("outputs/graficos/receita_por_mes.png", dpi=150)
plt.close()

# Exibir o gráfico exportado
caminho_grafico = "outputs/graficos/receita_por_mes.png"
print("Arquivo existe:", os.path.exists(caminho_grafico))

if os.path.exists(caminho_grafico):
    display(Image(filename=caminho_grafico))


# ============================================================
# --- Figura 2: Top 5 produtos por receita ---
# ============================================================

fig, ax = plt.subplots(figsize=(12, 6))

sns.barplot(
    data=metricas["top_produtos"],
    y="produto",
    x="receita_total",
    hue="produto",
    legend=False,
    palette=["tab:pink", "tab:cyan", "tab:purple", "tab:orange", "tab:red"],
    ax=ax
)

ax.set_title("Top 5 Produtos por Receita")
ax.set_xlabel("Receita Total (R$)")
ax.set_ylabel("Produto")

# Formatar os valores do eixo X com duas casas decimais
ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.2f}"))

plt.tight_layout()

# Salvar o gráfico
caminho_grafico = "outputs/graficos/top_produtos.png"
plt.savefig(caminho_grafico, dpi=150)
plt.close()

# Exibir o gráfico exportado
import os
from IPython.display import display, Image

print("Arquivo existe:", os.path.exists(caminho_grafico))

if os.path.exists(caminho_grafico):
    display(Image(filename=caminho_grafico))


# ============================================================
# --- Figura 3: Quantidade x Receita por Categoria ---
# ============================================================
 
fig, ax = plt.subplots(figsize=(12, 6))

# Criar o gráfico de dispersão, colorido por categoria
sns.scatterplot(
    data=df_rf04,
    x="quantidade",
    y="receita_total",
    hue="categoria",
    palette={
        "Computadores": "tab:pink",
        "Celulares": "tab:cyan",
        "Perifericos": "tab:purple"
    },
    ax=ax
)

# Configurar título e eixos
ax.set_title("Quantidade versus Receita por Categoria")
ax.set_xlabel("Quantidade")
ax.set_ylabel("Receita Total (R$)")

# Formatar os valores do eixo Y com duas casas decimais
ax.yaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.2f}")
)

# Exibir a legenda das categorias
ax.legend(title="Categoria")

# Ajustar o layout
plt.tight_layout()

# Salvar o gráfico
caminho_grafico = "outputs/graficos/quantidade_vs_receita.png"
plt.savefig(caminho_grafico, dpi=150)
plt.close()

# Verificar se o arquivo foi criado e exibir o gráfico exportado
print("Arquivo existe:", os.path.exists(caminho_grafico))

if os.path.exists(caminho_grafico):
    display(Image(filename=caminho_grafico))


# ============================================================
# --- Gráfico Receita Total por Região ---
# ============================================================

# Ordenar as regiões pela receita total
df_regiao = metricas["por_regiao"].sort_values(
    by="receita_total",
    ascending=True
)

fig, ax = plt.subplots(figsize=(12, 6))

ax.barh(
    df_regiao["regiao"],
    df_regiao["receita_total"],
    color=[
        "tab:green",
        "tab:orange",
        "tab:purple",
        "tab:cyan",
        "tab:pink"
    ],
    height=0.6
)

ax.set_title("Receita Total por Região")
ax.set_xlabel("Receita Total (R$)")
ax.set_ylabel("Região")

# Configurar a escala do eixo horizontal
ax.set_xlim(0, 400000)
ax.xaxis.set_major_locator(ticker.MultipleLocator(50000))
ax.xaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.0f}")
)

# Exibir os valores reais ao lado das barras
for container in ax.containers:
    ax.bar_label(
        container,
        labels=[
            f"R$ {valor:,.2f}"
            for valor in container.datavalues
        ],
        padding=5,
        fontsize=9
    )

plt.tight_layout()

# Salvar o gráfico
caminho_grafico = "outputs/graficos/receita_por_regiao.png"
plt.savefig(caminho_grafico, dpi=150)
plt.close()

# Verificar se o arquivo foi gerado e exibir o gráfico
print("Arquivo existe:", os.path.exists(caminho_grafico))

if os.path.exists(caminho_grafico):
    display(Image(filename=caminho_grafico))



# ============================================================
# --- Figura 4: Painel Resumo ---
# ============================================================
  
# Criar a figura com quatro gráficos (2 linhas e 2 colunas)
fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# Gráfico 1: Receita total por mês
axes[0, 0].plot(
    metricas["por_mes"]["mes"],
    metricas["por_mes"]["receita_total"],
    marker="o",
    linewidth=2,
    color="tab:pink",
    label="Receita total"
)

axes[0, 0].set_title("Receita Total por Mês")
axes[0, 0].set_xlabel("Mês")
axes[0, 0].set_ylabel("Receita Total (R$)")
axes[0, 0].yaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.0f}")
)
axes[0, 0].legend()

# Gráfico 2: Top 5 produtos por receita
sns.barplot(
    data=metricas["top_produtos"],
    y="produto",
    x="receita_total",
    hue="produto",
    legend=False,
    palette={
        "Notebook": "tab:pink",
        "Smartphone": "tab:cyan",
        "Tablet": "tab:purple",
        "Monitor": "tab:orange",
        "Headset": "tab:red"
    },
    ax=axes[0, 1]
)

axes[0, 1].set_title("Top 5 Produtos por Receita")
axes[0, 1].set_xlabel("Receita Total (R$)")
axes[0, 1].set_ylabel("Produto")
axes[0, 1].xaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.0f}")
)

# Gráfico 3: Quantidade versus receita por categoria
sns.scatterplot(
    data=df_rf04,
    x="quantidade",
    y="receita_total",
    hue="categoria",
    palette={
        "Computadores": "tab:pink",
        "Celulares": "tab:cyan",
        "Perifericos": "tab:purple"
    },
    ax=axes[1, 0]
)

axes[1, 0].set_title("Quantidade versus Receita por Categoria")
axes[1, 0].set_xlabel("Quantidade")
axes[1, 0].set_ylabel("Receita Total (R$)")
axes[1, 0].yaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.0f}")
)
axes[1, 0].legend(title="Categoria")

# Gráfico 4: Receita total por região (barras horizontais)
df_regiao = metricas["por_regiao"].sort_values(
    by="receita_total",
    ascending=True
)

cores_regiao = {
    "Centro-Oeste": "tab:pink",
    "Norte": "tab:cyan",
    "Nordeste": "tab:purple",
    "Sudeste": "tab:orange",
    "Sul": "tab:green"
}

axes[1, 1].barh(
    df_regiao["regiao"],
    df_regiao["receita_total"],
    color=[
        cores_regiao[regiao]
        for regiao in df_regiao["regiao"]
    ],
    height=0.6
)

axes[1, 1].set_title("Receita Total por Região")
axes[1, 1].set_xlabel("Receita Total (R$)")
axes[1, 1].set_ylabel("Região")

# Reservar espaço à direita para os valores das barras
axes[1, 1].set_xlim(0, 460000)

axes[1, 1].xaxis.set_major_locator(
    ticker.MultipleLocator(100000)
)
axes[1, 1].xaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.0f}")
)

# Exibir os valores reais ao lado das barras
for container in axes[1, 1].containers:
    axes[1, 1].bar_label(
        container,
        labels=[
            f"R$ {valor:,.2f}"
            for valor in container.datavalues
        ],
        padding=4,
        fontsize=9
    )

# Título geral do painel
fig.suptitle("SalesInsight PY - Painel Resumo", fontsize=16)

# Ajustar o layout para acomodar o título geral
plt.tight_layout(rect=[0, 0, 1, 0.95])

# Salvar o painel
caminho_grafico = "outputs/graficos/painel_resumo.png"
plt.savefig(caminho_grafico, dpi=150, bbox_inches="tight")
plt.close()

# Verificar se o arquivo foi criado e exibir a imagem exportada
print("Arquivo existe:", os.path.exists(caminho_grafico))

if os.path.exists(caminho_grafico):
    display(Image(filename=caminho_grafico))


# ============================================================
# GRÁFICO BÔNUS - B03 - RECEITA TOTAL POR MÊS E CATEGORIA
# ============================================================

fig, ax = plt.subplots(figsize=(12, 6))

for categoria, cor in zip(
    ["Celulares", "Computadores", "Perifericos"],
    ["tab:cyan", "tab:pink", "tab:purple"]
):
    ax.plot(
        tabela_mes_categoria.index.get_level_values("mes"),
        tabela_mes_categoria[categoria],
        marker="o",
        linewidth=2,
        color=cor,
        label=categoria
    )

ax.set_title("Receita Total por Mês e Categoria")
ax.set_xlabel("Mês")
ax.set_ylabel("Receita Total (R$)")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(
    tabela_mes_categoria.index.get_level_values("mes_nome")
)
ax.yaxis.set_major_formatter(
    ticker.StrMethodFormatter("R$ {x:,.0f}")
)
ax.legend(title="Categoria")

plt.tight_layout()

caminho_grafico = "outputs/graficos/receita_por_mes_categoria.png"
plt.savefig(caminho_grafico, dpi=150)
plt.close()

print("Arquivo existe:", os.path.exists(caminho_grafico))

if os.path.exists(caminho_grafico):
    display(Image(filename=caminho_grafico))


# ============================================================
# GRÁFICO EXTRA 1 - QUANTIDADE DE VENDAS POR DIA DA SEMANA
# ============================================================

# Definir as cores para dias úteis e fins de semana
cores_dias = [
    "tab:orange" if dia in ["Domingo", "Sábado"] else "tab:cyan"
    for dia in vendas_por_dia["dia_semana"]
]

# Criar o gráfico
fig, ax = plt.subplots(figsize=(12, 6))

barras = ax.bar(
    vendas_por_dia["dia_semana"],
    vendas_por_dia["quantidade_vendas"],
    color=cores_dias
)

ax.set_title("Quantidade de Vendas por Dia da Semana")
ax.set_xlabel("Dia da Semana")
ax.set_ylabel("Quantidade de Vendas")

# Exibir o valor sobre cada barra
ax.bar_label(barras, padding=3)

# Identificar as cores na legenda
from matplotlib.patches import Patch

ax.legend(
    handles=[
        Patch(facecolor="tab:cyan", label="Dias úteis"),
        Patch(facecolor="tab:orange", label="Fim de semana")
    ],
    title="Tipo de dia"
)

plt.tight_layout()

caminho_grafico = "outputs/graficos/vendas_por_dia_semana.png"
plt.savefig(caminho_grafico, dpi=150)
plt.close()

print("Arquivo existe:", os.path.exists(caminho_grafico))

if os.path.exists(caminho_grafico):
    display(Image(filename=caminho_grafico))


# ============================================================
# GRÁFICO EXTRA 2 - RECEITA POR CATEGORIA E PRODUTO
# ============================================================

# Associar cada produto à sua categoria
df_top_categoria = metricas["top_produtos"].merge(
    df_rf04[["produto", "categoria"]].drop_duplicates(),
    on="produto",
    how="left"
)

# Criar a figura
fig, ax = plt.subplots(figsize=(12, 6))

# Criar o gráfico de barras por produto e categoria
sns.barplot(
    data=df_top_categoria,
    x="produto",
    y="receita_total",
    hue="categoria",
    palette={
        "Computadores": "tab:pink",
        "Celulares": "tab:cyan",
        "Perifericos": "tab:purple"
    },
    ax=ax
)

# Definir título e rótulos dos eixos
ax.set_title("Receita por Categoria e Produto")
ax.set_xlabel("Produto")
ax.set_ylabel("Receita Total (R$)")

# Formatar os valores do eixo vertical
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.2f}"))

# Exibir os valores sobre as barras
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", padding=3, fontsize=9)

# Exibir a legenda
ax.legend(title="Categoria")

# Ajustar o layout
plt.tight_layout()

# Salvar o gráfico
caminho_grafico = "outputs/graficos/receita_categoria_produtos.png"
plt.savefig(caminho_grafico, dpi=150)
plt.close()

# Verificar se o arquivo foi gerado e exibir o gráfico
print("Arquivo existe:", os.path.exists(caminho_grafico))

if os.path.exists(caminho_grafico):
    display(Image(filename=caminho_grafico))


# ============================================================
# GRÁFICO EXTRA 3 - RECEITA POR TRIMESTRE E TOP 5 PRODUTOS
# ============================================================

# Identificar os cinco produtos com maior receita total
top5_produtos = metricas["top_produtos"]["produto"].tolist()

# Filtrar os dados dos cinco produtos
df_top5_trimestre = df_rf04[
    df_rf04["produto"].isin(top5_produtos)
].copy()

# Agrupar a receita total por trimestre e produto
receita_trimestre_produto = (
    df_top5_trimestre
    .groupby(["trimestre", "produto"])["receita_total"]
    .sum()
    .reset_index()
)

# Criar o gráfico
fig, ax = plt.subplots(figsize=(12, 6))

sns.barplot(
    data=receita_trimestre_produto,
    x="trimestre",
    y="receita_total",
    hue="produto",
    hue_order=top5_produtos,
    palette={
        "Notebook": "tab:pink",
        "Smartphone": "tab:cyan",
        "Tablet": "tab:purple",
        "Monitor": "tab:orange",
        "Headset": "tab:red"
    },
    ax=ax
)

ax.set_title("Receita por Trimestre e Top 5 Produtos")
ax.set_xlabel("Trimestre")
ax.set_ylabel("Receita Total (R$)")
ax.legend(title="Produto")

ax.yaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.0f}")
)

plt.tight_layout()

# Salvar o gráfico
caminho_grafico = (
    "outputs/graficos/receita_por_trimestre_top5.png"
)
plt.savefig(caminho_grafico, dpi=150)
plt.close()

# Verificar se o arquivo foi gerado e exibir o gráfico
print("Arquivo existe:", os.path.exists(caminho_grafico))

if os.path.exists(caminho_grafico):
    display(Image(filename=caminho_grafico))
