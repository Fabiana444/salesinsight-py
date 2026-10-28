import pandas as pd
import numpy as np
import random
import json
import os
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
def gerar_salvar_exibir_dataset(n_registros=200, seed=42):
    """
    Gera o dataset bruto, salva o arquivo CSV e exibe os primeiros registros.
    Retorna o DataFrame gerado.
    """
    df_bruto = gerar_dataset_vendas(n_registros, seed)
    df_bruto.to_csv("vendas.csv", index=False)

    print(f"Dataset gerado com {len(df_bruto)} registros.")
    print(df_bruto.head())

    return df_bruto

# Executar a geração do dataset
import os

caminho_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendas.csv")

if os.path.exists(caminho_csv):
    df_bruto = pd.read_csv(caminho_csv)
    print("Dataset original carregado.")
else:
    df_bruto = gerar_salvar_exibir_dataset()


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


# ============================================================
# RF03 - Tratar os dados (datetime)
# ============================================================

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

        diferencas = (texto_original.ne(texto_limpo) & ~(texto_original.isna() & texto_limpo.isna())).fillna(False)
        textos_alterados |= diferencas
        df_limpo[coluna] = texto_limpo

    registros_com_texto_alterado = int(textos_alterados.sum())

    # 2. Converter as datas e remover as inválidas
    datas_convertidas = pd.to_datetime(df_limpo["data_venda"], errors="coerce")

    datas_validas = int(datas_convertidas.notna().sum())
    datas_invalidas = int(datas_convertidas.isna().sum())

    df_limpo["data_venda"] = datas_convertidas
    df_limpo = df_limpo.dropna(subset=["data_venda"])

    # 3. Ajustar os tipos numéricos
    df_limpo["quantidade"] = df_limpo["quantidade"].astype(int)
    df_limpo["preco_unitario"] = (df_limpo["preco_unitario"].astype(float))

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


# ===============================================================
# RF04 - Criar Colunas Derivadas com Transformações Condicionais
# ===============================================================


# RF04 - Criar Colunas Derivadas com Transformações Condicionais

def criar_colunas_derivadas(df):
    """
    Cria as colunas derivadas do RF04 e organiza o DataFrame.
    Retorna um DataFrame com as colunas originais e derivadas.
    """
    # Criar uma cópia do DataFrame limpo para trabalhar no RF04
    df_rf04 = df.copy()

    # Reiniciar os índices após a remoção de linhas no RF03
    df_rf04 = df_rf04.reset_index(drop=True)

    # 1. Criar a coluna receita_total por operação vetorizada
    df_rf04["receita_total"] = (
        df_rf04["quantidade"] * df_rf04["preco_unitario"]
    )

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
    df_rf04["trimestre"] = (
        "Q" + df_rf04["data_venda"].dt.quarter.astype(str)
    )

    # 5. Criar a coluna ano extraído da data com .dt.year
    df_rf04["ano"] = df_rf04["data_venda"].dt.year

    # 6. Criar a coluna faixa_receita_item com classificação condicional
    condicoes = [
        df_rf04["receita_total"] < 500,
        (
            (df_rf04["receita_total"] >= 500)
            & (df_rf04["receita_total"] < 5000)
        ),
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

    return df_rf04


# Executar o RF04 com o DataFrame limpo do RF03
df_rf04 = criar_colunas_derivadas(df_limpo)


# Exibir os resultados do RF04
def exibir_resultados_rf04(df_rf04):
    """
    Exibe os resultados das colunas derivadas do RF04.
    Retorna o DataFrame exibido.
    """
    print("\n=== RF04 - COLUNAS DERIVADAS ===")
    print("Dimensões:", df_rf04.shape)
    print("\nColunas:", list(df_rf04.columns))
    print("\nPrimeiros registros:")
    print(
        df_rf04.head().assign(
            data_venda=df_rf04["data_venda"].head().dt.strftime("%d-%m-%Y")
        )
    )

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

    return df_rf04

# Executar a exibição dos resultados do RF04
df_rf04 = exibir_resultados_rf04(df_rf04)


# ============================================================
# RF08 - FUNÇÃO DE ORDEM SUPERIOR
# ============================================================

def processar_coluna(df, coluna, funcao_transformacao, nome_saida=None):
    """
    Aplica uma funcao de transformacao a uma coluna do DataFrame.
    Demonstra o uso de funcoes como argumento.
    """
    nome_saida = nome_saida or f"{coluna}_transformado"
    df[nome_saida] = df[coluna].apply(funcao_transformacao)

    return df


def testar_funcao_ordem_superior(df):
    """
    Testa a funcao de ordem superior com duas transformacoes.
    Retorna o DataFrame com as novas colunas.
    """
    df_rf08 = df.copy()

    df_rf08 = processar_coluna(
        df_rf08,
        "receita_total",
        lambda x: round(x / 1000, 2),
        nome_saida="receita_em_milhares"
    )

    df_rf08 = processar_coluna(
        df_rf08,
        "quantidade",
        lambda q: "Alto Volume" if q > 5 else "Baixo Volume",
        nome_saida="perfil_volume"
    )

    return df_rf08


def exibir_teste_funcao_ordem_superior(df):
    """
    Exibe os resultados do teste da funcao de ordem superior.
    Retorna o DataFrame exibido.
    """
    print("\n=== RF08 - TESTE DA FUNÇÃO DE ORDEM SUPERIOR ===")

    print(
        df[
            [
                "receita_total",
                "receita_em_milhares",
                "quantidade",
                "perfil_volume"
            ]
        ].head(10).to_string(index=False)
    )

    return df


# Executar o teste da função de ordem superior

df_rf08 = testar_funcao_ordem_superior(df_rf04)

df_rf08 = exibir_teste_funcao_ordem_superior(df_rf08)


# ============================================================
# B03 - Tabela cruzada mês x categoria
# ============================================================

def criar_tabela_mes_categoria(df):
    """
    Calcula e retorna a tabela cruzada de receita total
    por mês e categoria.
    """
    # Agrupar a receita total por mês e categoria
    receita_mes_categoria = df.groupby(
        ["mes", "mes_nome", "categoria"]
    )["receita_total"].sum().reset_index()

    # Criar a tabela cruzada
    tabela_mes_categoria = receita_mes_categoria.pivot(
        index=["mes", "mes_nome"],
        columns="categoria",
        values="receita_total"
    )

    return tabela_mes_categoria


def exibir_tabela_mes_categoria(tabela_mes_categoria):
    """
    Exibe a tabela cruzada de receita total por mês e categoria.
    """
    # Exibir a tabela cruzada
    print("\n=== B03 - RECEITA TOTAL POR MÊS E CATEGORIA ===")
    print(tabela_mes_categoria)

    return tabela_mes_categoria


# Executar a tabela cruzada B03
tabela_mes_categoria = criar_tabela_mes_categoria(df_rf04)
tabela_mes_categoria = exibir_tabela_mes_categoria(tabela_mes_categoria)



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
def exibir_metricas(metricas):
    """
    Exibe os resultados das métricas agregadas com groupby.
    Retorna as métricas exibidas.
    """
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

    return metricas


# Executar a exibição das métricas
metricas = exibir_metricas(metricas)


# ============================================================
# EXTRA 2 - ANALISAR VENDAS POR DIA DA SEMANA
# ============================================================

def analisar_vendas_por_dia_semana(df):
    """
    Analisa as vendas por dia da semana.
    Retorna o DataFrame com as novas colunas e o resumo das vendas.
    """
    # Criar uma cópia do DataFrame
    df_extra2 = df.copy()

    # Identificar o dia da semana
    df_extra2["dia_semana"] = df_extra2["data_venda"].dt.day_name()

    # Traduzir os nomes dos dias da semana para português
    dias_semana = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }

    df_extra2["dia_semana"] = df_extra2["dia_semana"].map(dias_semana)

    # Identificar se a venda ocorreu no fim de semana
    df_extra2["fim_de_semana"] = df_extra2["data_venda"].dt.dayofweek >= 5

    # Agrupar as vendas por dia da semana
    vendas_por_dia = df_extra2.groupby("dia_semana").agg(
        quantidade_vendas=("id_venda", "count"),
        receita_total=("receita_total", "sum")).reset_index()

    # Identificar o dia com maior e menor quantidade de vendas
    maior_fluxo = vendas_por_dia.loc[vendas_por_dia["quantidade_vendas"].idxmax()]

    menor_fluxo = vendas_por_dia.loc[vendas_por_dia["quantidade_vendas"].idxmin()]

    return df_extra2, vendas_por_dia, maior_fluxo, menor_fluxo


def exibir_analise_vendas_por_dia_semana(df_extra2, vendas_por_dia, maior_fluxo, menor_fluxo):
    """
    Exibe os resultados da análise de vendas por dia da semana.
    Retorna a tabela de vendas por dia.
    """
    # Exibir as novas colunas
    print("\n=== DIAS DA SEMANA E FIM DE SEMANA ===")
    print(df_extra2[["data_venda", "dia_semana", "fim_de_semana"]].head(10))

    # Conferir os tipos de dados
    print(df_extra2[["dia_semana", "fim_de_semana"]].dtypes)

    # Exibir as vendas por dia da semana
    print("\n=== VENDAS POR DIA DA SEMANA ===")
    print(vendas_por_dia)

    # Exibir o dia com maior quantidade de vendas
    print("\n=== DIA COM MAIOR QUANTIDADE DE VENDAS ===")
    print(maior_fluxo)

    # Exibir o dia com menor quantidade de vendas
    print("\n=== DIA COM MENOR QUANTIDADE DE VENDAS ===")
    print(menor_fluxo)

    return vendas_por_dia


# Executar a análise de vendas por dia da semana
df_extra2, vendas_por_dia, maior_fluxo, menor_fluxo = (analisar_vendas_por_dia_semana(df_rf04))

vendas_por_dia = exibir_analise_vendas_por_dia_semana(df_extra2, vendas_por_dia, maior_fluxo, menor_fluxo)


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


# Exibir os resultados da segmentação de clientes
def exibir_segmentacao_clientes(clientes_segmentados):
    """
    Exibe os 10 maiores clientes e a distribuição por segmento.
    Retorna o DataFrame de clientes segmentados.
    """
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

    return clientes_segmentados


# Executar a exibição da segmentação de clientes
clientes_segmentados = exibir_segmentacao_clientes(clientes_segmentados)


# ============================================================
# RF07 - CRIAR VISUALIZAÇÕES COM MATPLOTLIB
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
def criar_grafico_receita_por_mes(metricas):
    """
    Cria e salva o gráfico de receita total por mês.
    Retorna o caminho do arquivo gerado.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(metricas["por_mes"]["mes"], metricas["por_mes"]["receita_total"], marker="o", markersize=7, linewidth=2.5, color="tab:pink", markerfacecolor="tab:cyan", markeredgecolor="white", label="Receita total")
    ax.set_title("Receita Total por Mês")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Receita Total (R$)")
    ax.legend()
    plt.tight_layout()

    caminho_grafico = "outputs/graficos/receita_por_mes.png"
    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    # Exibir o gráfico exportado
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar a Figura 1
caminho_grafico = criar_grafico_receita_por_mes(metricas)



# ============================================================
# --- Figura 2: Top 5 produtos por receita ---
# ============================================================

def criar_grafico_top_produtos(metricas):
    """
    Cria e salva o gráfico dos top 5 produtos por receita.
    Retorna o caminho do arquivo gerado.
    """
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
    plt.show()
    plt.close()

    # Exibir o gráfico exportado
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar a Figura 2
caminho_grafico = criar_grafico_top_produtos(metricas)


# ============================================================
# --- Figura 3: Quantidade x Receita por Categoria ---
# ============================================================

def criar_grafico_quantidade_vs_receita(df_rf04):
    """
    Cria e salva o gráfico de quantidade versus receita por categoria.
    Retorna o caminho do arquivo gerado.
    """

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
    plt.show()
    plt.close()

    # Verificar se o arquivo foi criado e exibir o gráfico exportado
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar a Figura 3
caminho_grafico = criar_grafico_quantidade_vs_receita(df_rf04)


# ============================================================
# --- Gráfico Receita Total por Região ---
# ============================================================

def criar_grafico_receita_por_regiao(metricas):
    """
    Cria e salva o gráfico de receita total por região.
    Retorna o caminho do arquivo gerado.
    """

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
    plt.show()
    plt.close()

    # Verificar se o arquivo foi gerado e exibir o gráfico
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar o gráfico de receita total por região
caminho_grafico = criar_grafico_receita_por_regiao(metricas)


# ============================================================
# --- Figura 4: Painel Resumo ---
# ============================================================

def criar_painel_resumo(metricas, df_rf04):
    """
    Cria e salva o painel resumo com quatro gráficos.
    Retorna o caminho do arquivo gerado.
    """

    # Criar a figura com quatro gráficos (2 linhas e 2 colunas)
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))

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
    plt.show()
    plt.close()

    # Verificar se o arquivo foi criado e exibir a imagem exportada
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar a Figura 4
caminho_grafico = criar_painel_resumo(metricas, df_rf04)


# ============================================================
# GRÁFICO BÔNUS - B03 - RECEITA TOTAL POR MÊS E CATEGORIA
# ============================================================

def criar_grafico_receita_por_mes_categoria(tabela_mes_categoria):
    """
    Cria e salva o gráfico de receita total por mês e categoria.
    Retorna o caminho do arquivo gerado.
    """

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
    plt.show()
    plt.close()

    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar o gráfico bônus B03
caminho_grafico = criar_grafico_receita_por_mes_categoria(tabela_mes_categoria)


# ============================================================
# GRÁFICO EXTRA 1 - QUANTIDADE DE VENDAS POR DIA DA SEMANA
# ============================================================

def criar_grafico_vendas_por_dia_semana(vendas_por_dia):
    """
    Cria e salva o gráfico de quantidade de vendas por dia da semana.
    Retorna o caminho do arquivo gerado.
    """

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
    plt.show()
    plt.close()

    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar o gráfico extra 1
caminho_grafico = criar_grafico_vendas_por_dia_semana(vendas_por_dia)


# ============================================================
# GRÁFICO EXTRA 2 - RECEITA POR CATEGORIA E PRODUTO
# ============================================================

def criar_grafico_receita_categoria_produtos(metricas, df_rf04):
    """
    Cria e salva o gráfico de receita por categoria e produto.
    Retorna o caminho do arquivo gerado.
    """

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
    plt.show()
    plt.close()

    # Verificar se o arquivo foi gerado e exibir o gráfico
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar o gráfico extra 2
caminho_grafico = criar_grafico_receita_categoria_produtos(metricas, df_rf04)


# ============================================================
# GRÁFICO EXTRA 3 - RECEITA POR TRIMESTRE E TOP 5 PRODUTOS
# ============================================================

def criar_grafico_receita_por_trimestre_top5(df_rf04, metricas):
    """
    Cria e salva o gráfico de receita por trimestre e top 5 produtos.
    Retorna o caminho do arquivo gerado.
    """

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
    plt.show()
    plt.close()

    # Verificar se o arquivo foi gerado e exibir o gráfico
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar o gráfico extra 3
caminho_grafico = criar_grafico_receita_por_trimestre_top5(df_rf04, metricas)


# ============================================================
# GRÁFICO EXTRA 4 - RECEITA POR SEGMENTO DE CLIENTE E CATEGORIA DE PRODUTO
# ============================================================

def criar_grafico_receita_segmento_categoria(df_rf04, clientes_segmentados):
    """
    Cria e salva o gráfico de receita por segmento de cliente e categoria de produto.
    Retorna o caminho do arquivo gerado.
    """

    # Cruzar as vendas com o segmento de cada cliente
    df_segmento_categoria = df_rf04.merge(
        clientes_segmentados[["cliente", "segmento"]],
        on="cliente",
        how="left"
    )

    # Calcular a receita total por segmento de cliente e categoria de produto
    receita_segmento_categoria = (
        df_segmento_categoria
        .groupby(["segmento", "categoria"])["receita_total"]
        .sum()
        .reset_index()
    )

    # Definir a ordem dos segmentos e das categorias
    ordem_segmentos = ["Bronze", "Prata", "Ouro"]
    ordem_categorias = ["Computadores", "Celulares", "Perifericos"]

    # Criar o gráfico
    fig, ax = plt.subplots(figsize=(12, 6))

    sns.barplot(
        data=receita_segmento_categoria,
        x="segmento",
        y="receita_total",
        hue="categoria",
        order=ordem_segmentos,
        hue_order=ordem_categorias,
        palette={
            "Computadores": "tab:pink",
            "Celulares": "tab:cyan",
            "Perifericos": "tab:purple"
        },
        ax=ax
    )

    ax.set_title("Receita por Segmento de Cliente e Categoria de Produto")
    ax.set_xlabel("Segmento de Cliente")
    ax.set_ylabel("Receita Total (R$)")
    ax.yaxis.set_major_formatter(
        ticker.StrMethodFormatter("R$ {x:,.0f}")
    )
    ax.legend(title="Categoria de Produto")

    plt.tight_layout()

    caminho_grafico = (
        "outputs/graficos/"
        "receita_segmento_cliente_categoria_produto.png"
    )

    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar o gráfico extra 4
caminho_grafico = criar_grafico_receita_segmento_categoria(df_rf04, clientes_segmentados)


# ==============================================================
# GRÁFICO EXTRA 5 - QUANTIDADE DE CLIENTES POR REGIÃO E SEGMENTO
# ==============================================================

def criar_grafico_clientes_regiao_segmento(df_rf04, clientes_segmentados):
    """
    Cria e salva o gráfico de quantidade de clientes por região e segmento.
    Retorna o caminho do arquivo gerado.
    """

    # Criar a tabela com a quantidade de clientes por região e segmento
    df_segmento_regiao = df_rf04.merge(
        clientes_segmentados[["cliente", "segmento"]],
        on="cliente",
        how="left"
    )

    clientes_por_regiao = (
        df_segmento_regiao
        .groupby(["regiao", "segmento"])["cliente"]
        .nunique()
        .unstack(fill_value=0)
    )

    # Garantir a ordem dos segmentos
    ordem_segmentos = ["Bronze", "Prata", "Ouro"]
    clientes_por_regiao = clientes_por_regiao.reindex(
        columns=ordem_segmentos,
        fill_value=0
    )

    # Criar o gráfico de barras empilhadas
    fig, ax = plt.subplots(figsize=(12, 7))

    cores_segmentos = {
        "Bronze": "tab:orange",
        "Prata": "tab:cyan",
        "Ouro": "tab:pink"
    }

    base = [0] * len(clientes_por_regiao)
    posicoes = list(range(len(clientes_por_regiao)))

    for segmento in ordem_segmentos:
        valores = clientes_por_regiao[segmento].values

        barras = ax.bar(
            posicoes,
            valores,
            bottom=base,
            color=cores_segmentos[segmento],
            label=segmento,
            width=0.65
        )

        # Exibir a quantidade dentro de cada segmento
        for barra, valor, base_inferior in zip(barras, valores, base):
            if valor > 0:
                ax.text(
                    barra.get_x() + barra.get_width() / 2,
                    base_inferior + valor / 2,
                    str(int(valor)),
                    ha="center",
                    va="center",
                    fontsize=10,
                    fontweight="bold"
                )

        base = [b + v for b, v in zip(base, valores)]

    # Configurar o gráfico
    ax.set_title("Quantidade de Clientes por Região e Segmento")
    ax.set_xlabel("Região")
    ax.set_ylabel("Quantidade de Clientes")
    ax.set_xticks(posicoes)
    ax.set_xticklabels(clientes_por_regiao.index)
    ax.legend(title="Segmento de Cliente")
    ax.set_ylim(bottom=0)

    plt.tight_layout()

    # Salvar o gráfico
    caminho_grafico = (
        "outputs/graficos/quantidade_clientes_regiao_segmento.png"
    )

    plt.savefig(caminho_grafico, dpi=150, bbox_inches="tight")
    plt.show()
    plt.close()

    # Exibir o gráfico salvo
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar o gráfico extra 5
caminho_grafico = criar_grafico_clientes_regiao_segmento(df_rf04, clientes_segmentados)

 
# ======================================================================
# GRÁFICO BÔNUS - B04 - MAPA DE CALOR DA RECEITA POR PRODUTO E CATEGORIA
# ======================================================================

def criar_mapa_calor_receita_produto_categoria(df_rf04):
    """
    Cria e salva o mapa de calor da receita por produto e categoria.
    Retorna o caminho do arquivo gerado.
    """

    # Calcular a receita total por categoria e produto
    receita_categoria_produto = (
        df_rf04
        .groupby(["categoria", "produto"])["receita_total"]
        .sum()
        .reset_index()
    )

    # Organizar os dados para o mapa de calor
    tabela_calor = receita_categoria_produto.pivot(
        index="produto",
        columns="categoria",
        values="receita_total"
    )

    # Criar o mapa de calor
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.heatmap(
        tabela_calor,
        annot=True,
        fmt=".2f",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="white",
        mask=tabela_calor.isna(),
        cbar_kws={"label": "Receita total (R$)"},
        ax=ax
    )

    ax.set_title("Mapa de Calor da Receita Total por Produto e Categoria")
    ax.set_xlabel("Categoria")
    ax.set_ylabel("Produto")

    fig.tight_layout()

    caminho_grafico = (
        "outputs/graficos/mapa_calor_receita_produto_categoria.png"
    )

    fig.savefig(
        caminho_grafico,
        dpi=150,
        bbox_inches="tight"
    )

    plt.show()
    plt.close(fig)

    # Verificar se o arquivo foi gerado e exibir o gráfico
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# Executar o gráfico bônus B04
caminho_grafico = criar_mapa_calor_receita_produto_categoria(df_rf04)


# ============================================================
# RF09 - Exportar Resultados em CSV e JSON
# ============================================================

def exportar_resultados(metricas, clientes, estatisticas):
    """Exporta os resultados do projeto em CSV e JSON."""

    from decimal import Decimal, ROUND_DOWN

    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_outputs = os.path.join(pasta_projeto, "outputs")
    os.makedirs(pasta_outputs, exist_ok=True)

    # Preparar cópias dos DataFrames para exportação
    metricas_exportacao = metricas["por_mes"].copy()
    clientes_exportacao = clientes.copy()

    # Identificar as colunas que contêm valores monetários
    termos_monetarios = (
        "receita",
        "preco",
        "preço",
        "ticket",
        "gasto",
        "faturamento",
        "valor"
    )

    # Formatar os valores monetários para visualização, sem arredondar
    def formatar_valor_monetario(valor):
        if pd.isna(valor):
            return ""

        valor_decimal = Decimal(str(valor)).quantize(
            Decimal("0.01"),
            rounding=ROUND_DOWN
        )

        valor_formatado = f"{valor_decimal:,.2f}"

        return (
            valor_formatado
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    # Exportar métricas por mês
    colunas_monetarias = [
        coluna
        for coluna in metricas_exportacao.columns
        if any(
            termo in str(coluna).lower()
            for termo in termos_monetarios
        )
        and pd.api.types.is_numeric_dtype(
            metricas_exportacao[coluna]
        )
    ]

    for coluna in colunas_monetarias:
        metricas_exportacao[coluna] = (
            metricas_exportacao[coluna]
            .apply(formatar_valor_monetario)
        )

    metricas_exportacao.to_csv(
        os.path.join(pasta_outputs, "metricas_por_mes.csv"),
        index=False,
        encoding="utf-8-sig"
    )

    # Exportar segmentação de clientes
    colunas_monetarias = [
        coluna
        for coluna in clientes_exportacao.columns
        if any(
            termo in str(coluna).lower()
            for termo in termos_monetarios
        )
        and pd.api.types.is_numeric_dtype(
            clientes_exportacao[coluna]
        )
    ]

    for coluna in colunas_monetarias:
        clientes_exportacao[coluna] = (
            clientes_exportacao[coluna]
            .apply(formatar_valor_monetario)
        )

    clientes_exportacao.to_csv(
        os.path.join(pasta_outputs, "segmentacao_clientes.csv"),
        index=False,
        encoding="utf-8-sig"
    )

    # Preparar os valores numéricos para gravação no JSON
    serializavel = {
        chave: round(float(valor), 2)
        for chave, valor in estatisticas.items()
    }

    caminho = os.path.join(pasta_outputs, "estatisticas_gerais.json")

    # Gravar as estatísticas gerais em JSON
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(
            serializavel,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    # Ler o JSON novamente para confirmar a gravação
    with open(caminho, "r", encoding="utf-8") as arquivo:
        estatisticas_lidas = json.load(arquivo)

    # Exibir as estatísticas gerais
    print("\n=== RF09 - ESTATÍSTICAS GERAIS EXPORTADAS ===")

    for chave, valor in estatisticas_lidas.items():
        if (
            "receita_total" in chave
            or "ticket_medio" in chave
            or "gasto_medio_cliente" in chave
        ):
            valor_formatado = (
                f"R$ {valor:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )
            print(f"{chave}: {valor_formatado}")
        else:
            print(f"{chave}: {valor}")

    return estatisticas_lidas


# Preparar as estatísticas gerais
estatisticas = {}

# 1. Estatísticas gerais do período
receita_total_periodo = metricas["por_mes"]["receita_total"].sum()
quantidade_total_vendida = metricas["por_mes"]["quantidade_vendida"].sum()
total_vendas = metricas["por_mes"]["n_vendas"].sum()

estatisticas["receita_total_periodo"] = receita_total_periodo
estatisticas["quantidade_total_vendida"] = quantidade_total_vendida
estatisticas["total_vendas"] = total_vendas
estatisticas["ticket_medio_geral"] = (
    receita_total_periodo / total_vendas
)

# 2. Estatísticas por trimestre
metricas_por_trimestre = (
    df_rf04.groupby("trimestre")
    .agg(
        receita_total=("receita_total", "sum"),
        quantidade_vendida=("quantidade", "sum"),
        n_vendas=("id_venda", "count")
    )
    .reset_index()
)

for _, linha in metricas_por_trimestre.iterrows():
    trimestre = linha["trimestre"]

    estatisticas[f"total_vendas_{trimestre}"] = linha["n_vendas"]

    estatisticas[f"ticket_medio_{trimestre}"] = (
        linha["receita_total"] / linha["n_vendas"]
    )

# 3. Gasto médio por cliente em cada segmento
gasto_medio_segmento = (
    clientes_segmentados
    .groupby("segmento")["total_gasto"]
    .mean()
)

for segmento, valor in gasto_medio_segmento.items():
    estatisticas[f"gasto_medio_cliente_{segmento}"] = valor

# 4. Ticket médio por segmento de cliente e categoria de produto
df_segmento_categoria = df_rf04.merge(
    clientes_segmentados[["cliente", "segmento"]],
    on="cliente",
    how="left"
)

metricas_segmento_categoria = (
    df_segmento_categoria
    .groupby(["segmento", "categoria"])
    .agg(
        receita_total=("receita_total", "sum"),
        n_vendas=("id_venda", "count")
    )
    .reset_index()
)

metricas_segmento_categoria["ticket_medio"] = (
    metricas_segmento_categoria["receita_total"]
    / metricas_segmento_categoria["n_vendas"]
)

for _, linha in metricas_segmento_categoria.iterrows():
    segmento = linha["segmento"]
    categoria = linha["categoria"]

    chave = f"ticket_medio_{segmento}_{categoria}"
    estatisticas[chave] = linha["ticket_medio"]

# Executar a exportação dos resultados
estatisticas_lidas = exportar_resultados(
    metricas,
    clientes_segmentados,
    estatisticas
)