import pandas as pd
import numpy as np
import random
import json
import os
from datetime import datetime, timedelta


# ==================================
# RF01 - Gerar o dataset no código
# ==================================

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

        # Sujeira proposital para testar a limpeza.
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



def gerar_salvar_exibir_dataset(n_registros=200, seed=42):
    """
    Gera o dataset bruto, salva o arquivo CSV e exibe os primeiros registros.
    Retorna o DataFrame gerado.
    """
    df_bruto = gerar_dataset_vendas(n_registros, seed)

    caminho_csv = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "vendas.csv"
    )

    df_bruto.to_csv(caminho_csv, index=False)

    print(f"Dataset gerado com {len(df_bruto)} registros.")
    print(df_bruto.head())

    return df_bruto

# ============================================================
# Executar a geração ou carregar o dataset existente
# ============================================================

caminho_csv = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "vendas.csv"
)

if os.path.exists(caminho_csv):
    df_bruto = pd.read_csv(caminho_csv)
    print("Dataset original carregado.")
else:
    df_bruto = gerar_salvar_exibir_dataset()


# =========================================
# RF02 - Inspecionar e Descrever os Dados
# =========================================

def inspecionar_dados(df):
    """Exibe as informacoes estruturais do DataFrame."""
    print("\n=== INSPECAO INICIAL DO DATASET ===")
    print(f"Shape: {df.shape}")
    print(f"\nColunas: {list(df.columns)}")
    print(f"\nTipos de dados:\n{df.dtypes}")
    print(f"\nValores nulos por coluna:\n{df.isnull().sum()}")
    print(f"\nPrimeiros registros:\n{df.head()}")

    return df


# ============================================================
# RF03 - TRATAR OS DADOS (DATETIME)
# ============================================================

def tratar_dados(df):
    """
    Trata o DataFrame de vendas.

    Executa:
        - Remoção de espaços extras nos textos.
        - Conversão de datas e remoção de datas inválidas.
        - Ajuste dos tipos numéricos.
        - Geração do relatório de limpeza.

    Retorna:
        (df_limpo, relatorio)
    """

    # Preservar o DataFrame original.
    df_limpo = df.copy()

    registros_iniciais = len(df_limpo)

    # Guardar os valores originais para comparar alterações reais.
    valores_originais = df.copy()

    # 1. REMOVER ESPAÇOS EXTRAS DOS TEXTOS
    
    colunas_texto = [
        "cliente",
        "produto",
        "categoria",
        "regiao"
    ]

    textos_alterados = pd.Series(
        False,
        index=df_limpo.index
    )

    for coluna in colunas_texto:
        texto_original = df_limpo[coluna]

        # Preservar valores ausentes sem transformá-los em texto.
        texto_limpo = texto_original.str.strip()

        diferencas = (
            texto_original.ne(texto_limpo)
            & ~(
                texto_original.isna()
                & texto_limpo.isna()
            )
        ).fillna(False)

        textos_alterados |= diferencas
        df_limpo[coluna] = texto_limpo

    registros_com_texto_alterado = int(
        textos_alterados.sum()
    )

    # 2. CONVERTER DATAS E REMOVER DATAS INVÁLIDAS
   
    datas_originais = df_limpo["data_venda"]

    datas_convertidas = pd.to_datetime(
        datas_originais,
        errors="coerce"
    )

    datas_validas = int(datas_convertidas.notna().sum())
    datas_invalidas = int(datas_convertidas.isna().sum())

    # Contar datas válidas cujo valor precisou ser interpretado
    # ou normalizado para datetime, sem contar apenas a mudança
    # de tipo como alteração de valor.
    datas_originais_convertidas = pd.to_datetime(
        datas_originais,
        errors="coerce"
    )

    conversao_data = int(
        datas_originais.notna().sum()
        if not pd.api.types.is_datetime64_any_dtype(
            datas_originais
        )
        else 0
    )

    df_limpo["data_venda"] = datas_convertidas

    # Remover somente registros sem uma data válida.
    df_limpo = df_limpo.dropna(
        subset=["data_venda"]
    ).copy()

    # 3. AJUSTAR OS TIPOS NUMÉRICOS
    
    quantidade_original = df_limpo["quantidade"].copy()
    preco_original = df_limpo["preco_unitario"].copy()

    quantidade_convertida = pd.to_numeric(
        quantidade_original,
        errors="raise"
    )

    preco_convertido = pd.to_numeric(
        preco_original,
        errors="raise"
    )

    # Verificar se houve mudança de representação/tipo.
    conversao_quantidade = int(
        len(df_limpo)
        if not pd.api.types.is_integer_dtype(
            quantidade_original.dtype
        )
        else 0
    )

    conversao_preco = int(
        len(df_limpo)
        if not pd.api.types.is_float_dtype(
            preco_original.dtype
        )
        else 0
    )

    df_limpo["quantidade"] = quantidade_convertida.astype(int)
    df_limpo["preco_unitario"] = preco_convertido.astype(float)

    # 4. IDENTIFICAR REGISTROS ALTERADOS
    
    # Considerar somente os registros que permaneceram após
    # a remoção de datas inválidas.
    textos_finais_alterados = textos_alterados.loc[
        df_limpo.index
    ]

    registros_alterados = textos_finais_alterados.copy()

    # Comparar os valores numéricos antes e depois da limpeza.
    # Mudança apenas de tipo não significa, por si só,
    # mudança de valor.
    for coluna in ["quantidade", "preco_unitario"]:
        valores_antes = pd.to_numeric(
            valores_originais.loc[df_limpo.index, coluna],
            errors="coerce"
        )

        valores_depois = df_limpo[coluna]

        diferencas = (
            valores_antes.ne(valores_depois)
            & ~(
                valores_antes.isna()
                & valores_depois.isna()
            )
        ).fillna(False)

        registros_alterados |= diferencas

    # Registros com datas válidas são considerados alterados
    # quando o conteúdo original não era um datetime.
    # Essa informação é separada das alterações de texto e
    # dos valores numéricos no relatório.
    datas_originais_finais = valores_originais.loc[
        df_limpo.index,
        "data_venda"
    ]

    datas_ja_datetime = pd.api.types.is_datetime64_any_dtype(
        datas_originais_finais.dtype
    )

    if not datas_ja_datetime:
        # A conversão do tipo, sozinha, não marca o registro
        # como alterado em registros_convertidos_de_tipo.
        pass

    registros_convertidos_de_tipo = int(
        registros_alterados.sum()
    )

    registros_sem_alteracao = int(
        (~registros_alterados).sum()
    )
    
    # 5. MONTAR O RELATÓRIO DE LIMPEZA
    
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
        # 6. EXIBIR O RELATÓRIO
   
    print("\n=== RELATÓRIO DE LIMPEZA — RF03 ===")
    print("Registros iniciais:", registros_iniciais)

    print("\nConversões por motivo:")
    print("Datas válidas convertidas para datetime:", conversao_data)
    print("Registros convertidos para quantidade int:", conversao_quantidade)
    print("Registros convertidos para preço float:", conversao_preco)
    print("Registros com texto alterado:", registros_com_texto_alterado)

    print("\nResultado da limpeza:")
    print("Registros alterados nos valores:", registros_convertidos_de_tipo)
    print("Registros sem alteração nos valores:", registros_sem_alteracao)
    print("Datas inválidas encontradas:", datas_invalidas)
    print("Registros removidos:", registros_removidos)
    print("Registros finais:", registros_finais)

    return df_limpo, relatorio


# ===============================================================
# RF04 - Criar Colunas Derivadas com Transformações Condicionais
# ===============================================================

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

    # 2. Criar a coluna mes (nº do mês) extraída da data com .dt.month
    df_rf04["mes"] = df_rf04["data_venda"].dt.month

    # 3. Criar a coluna nome do mês em português com um dicionário de mapeamento
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


# ===============================================================
# RF04 - Exibir resultados
# ===============================================================

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
        receita_total=("receita_total", "sum")
    ).reset_index()

    # Identificar o dia com maior e menor quantidade de vendas
    maior_fluxo = vendas_por_dia.loc[
        vendas_por_dia["quantidade_vendas"].idxmax()
    ]

    menor_fluxo = vendas_por_dia.loc[
        vendas_por_dia["quantidade_vendas"].idxmin()
    ]

    return df_extra2, vendas_por_dia, maior_fluxo, menor_fluxo


def exibir_analise_vendas_por_dia_semana(
    df_extra2,
    vendas_por_dia,
    maior_fluxo,
    menor_fluxo
):
    """
    Exibe os resultados da análise de vendas por dia da semana.
    Retorna a tabela de vendas por dia.
    """
    # Exibir as novas colunas
    print("\n=== DIAS DA SEMANA E FIM DE SEMANA ===")
    print(
        df_extra2[
            ["data_venda", "dia_semana", "fim_de_semana"]
        ].head(10)
    )

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
pasta_projeto = os.path.dirname(os.path.abspath(__file__))
pasta_graficos = os.path.join(
    pasta_projeto,
    "outputs",
    "graficos"
)
os.makedirs(pasta_graficos, exist_ok=True)


# --- Figura 1: Receita total por mês ---
def criar_grafico_receita_por_mes(metricas):
    """
    Cria e salva o gráfico de receita total por mês.
    Retorna o caminho do arquivo gerado.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        metricas["por_mes"]["mes"],
        metricas["por_mes"]["receita_total"],
        marker="o",
        markersize=7,
        linewidth=2.5,
        color="tab:pink",
        markerfacecolor="tab:cyan",
        markeredgecolor="white",
        label="Receita total"
    )
    ax.set_title("Receita Total por Mês")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Receita Total (R$)")
    ax.legend()
    plt.tight_layout()

    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "receita_por_mes.png"
    )

    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    # Exibir o gráfico exportado
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


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
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "top_produtos.png"
    )

    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    # Exibir o gráfico exportado
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


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
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "quantidade_vs_receita.png"
    )

    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    # Verificar se o arquivo foi criado e exibir o gráfico exportado
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


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
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "receita_por_regiao.png"
    )

    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    # Verificar se o arquivo foi gerado e exibir o gráfico
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


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
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "painel_resumo.png"
    )

    plt.savefig(
        caminho_grafico,
        dpi=150,
        bbox_inches="tight"
    )
    plt.show()
    plt.close()

    # Verificar se o arquivo foi criado e exibir a imagem exportada
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


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

    # Salvar o gráfico na pasta outputs/graficos do projeto
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "receita_por_mes_categoria.png"
    )

    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


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

    # Salvar o gráfico na pasta outputs/graficos do projeto
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "vendas_por_dia_semana.png"
    )

    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico

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

    # Salvar o gráfico na pasta outputs/graficos do projeto
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "receita_categoria_produtos.png"
    )

    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    # Verificar se o arquivo foi gerado e exibir o gráfico
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


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

    # Salvar o gráfico na pasta outputs/graficos do projeto
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "receita_por_trimestre_top5.png"
    )

    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    # Verificar se o arquivo foi gerado e exibir o gráfico
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


# ========================================================================
# GRÁFICO EXTRA 4 - RECEITA POR SEGMENTO DE CLIENTE E CATEGORIA DE PRODUTO
# ========================================================================

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

    # Salvar o gráfico na pasta outputs/graficos do projeto
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "receita_segmento_cliente_categoria_produto.png"
    )

    plt.savefig(caminho_grafico, dpi=150)
    plt.show()
    plt.close()

    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico


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

    # Salvar o gráfico na pasta outputs/graficos do projeto
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "quantidade_clientes_regiao_segmento.png"
    )

    plt.savefig(caminho_grafico, dpi=150, bbox_inches="tight")
    plt.show()
    plt.close()

    # Exibir o gráfico salvo
    print("Arquivo existe:", os.path.exists(caminho_grafico))

    if os.path.exists(caminho_grafico):
        display(Image(filename=caminho_grafico))

    return caminho_grafico

 
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

    # Salvar o gráfico na pasta outputs/graficos do projeto
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_grafico = os.path.join(
        pasta_projeto,
        "outputs",
        "graficos",
        "mapa_calor_receita_produto_categoria.png"
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


# ============================================================
# RF09 - PREPARAR ESTATÍSTICAS GERAIS E EXPORTAR RESULTADOS
# ============================================================

import os
import json
import numpy as np


def preparar_estatisticas_gerais(
    metricas,
    df_rf04,
    clientes_segmentados
):
    """
    Prepara as estatísticas gerais do SalesInsight PY.
    """

    estatisticas = {}

    # 1. ESTATÍSTICAS GERAIS DO PERÍODO
    receita_total_periodo = (
        metricas["por_mes"]["receita_total"].sum()
    )

    quantidade_total_vendida = (
        metricas["por_mes"]["quantidade_vendida"].sum()
    )

    total_vendas = (
        metricas["por_mes"]["n_vendas"].sum()
    )

    estatisticas["receita_total_periodo"] = receita_total_periodo
    estatisticas["quantidade_total_vendida"] = quantidade_total_vendida
    estatisticas["total_vendas"] = total_vendas

    estatisticas["ticket_medio_geral"] = (
        receita_total_periodo / total_vendas
        if total_vendas > 0
        else 0.0
    )

    # 2. ESTATÍSTICAS POR TRIMESTRE
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

        vendas_trimestre = linha["n_vendas"]

        estatisticas[f"total_vendas_{trimestre}"] = (
            vendas_trimestre
        )

        estatisticas[f"ticket_medio_{trimestre}"] = (
            linha["receita_total"] / vendas_trimestre
            if vendas_trimestre > 0
            else 0.0
        )

    # 3. GASTO MÉDIO POR CLIENTE EM CADA SEGMENTO
    gasto_medio_segmento = (
        clientes_segmentados
        .groupby("segmento")["total_gasto"]
        .mean()
    )

    for segmento, valor in gasto_medio_segmento.items():
        estatisticas[f"gasto_medio_cliente_{segmento}"] = valor

    # 4. TICKET MÉDIO POR SEGMENTO E CATEGORIA
    clientes_para_merge = (
        clientes_segmentados[["cliente", "segmento"]]
        .drop_duplicates(subset=["cliente"])
    )

    df_segmento_categoria = df_rf04.merge(
        clientes_para_merge,
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
        / metricas_segmento_categoria["n_vendas"].replace(0, np.nan)
    )

    metricas_segmento_categoria["ticket_medio"] = (
        metricas_segmento_categoria["ticket_medio"].fillna(0)
    )

    for _, linha in metricas_segmento_categoria.iterrows():
        segmento = linha["segmento"]
        categoria = linha["categoria"]

        chave = f"ticket_medio_{segmento}_{categoria}"

        estatisticas[chave] = linha["ticket_medio"]

    return estatisticas



# ============================================================
# RF09 - EXPORTAR RESULTADOS
# ============================================================

def exportar_resultados(
    metricas,
    clientes_segmentados,
    estatisticas
):
    """
    Exporta os resultados para a pasta outputs e exibe
    as estatísticas gerais no terminal.
    """

    pasta_projeto = os.path.dirname(
        os.path.abspath(__file__)
    )

    pasta_outputs = os.path.join(
        pasta_projeto,
        "outputs"
    )

    os.makedirs(
        pasta_outputs,
        exist_ok=True
    )

    # 1. EXPORTAR MÉTRICAS MENSAIS
    caminho_metricas = os.path.join(
        pasta_outputs,
        "metricas_por_mes.csv"
    )

    metricas["por_mes"].to_csv(
        caminho_metricas,
        index=False,
        encoding="utf-8-sig"
    )

    # 2. EXPORTAR SEGMENTAÇÃO DE CLIENTES
    caminho_segmentacao = os.path.join(
        pasta_outputs,
        "segmentacao_clientes.csv"
    )

    clientes_segmentados.to_csv(
        caminho_segmentacao,
        index=False,
        encoding="utf-8-sig"
    )

    # 3. PREPARAR VALORES PARA EXPORTAÇÃO JSON
    estatisticas_json = {}

    for chave, valor in estatisticas.items():
        if isinstance(valor, np.generic):
            valor = valor.item()

        estatisticas_json[chave] = valor

    # 4. EXPORTAR ESTATÍSTICAS GERAIS EM JSON
    caminho_estatisticas = os.path.join(
        pasta_outputs,
        "estatisticas_gerais.json"
    )

    with open(
        caminho_estatisticas,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            estatisticas_json,
            arquivo,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    # 5. EXIBIR TODAS AS ESTATÍSTICAS NO TERMINAL
    print("\n=== RF09 - ESTATÍSTICAS GERAIS EXPORTADAS ===")

    for chave, valor in estatisticas.items():

        if isinstance(valor, np.generic):
            valor = valor.item()

        if any(
            termo in chave
            for termo in [
                "receita_total",
                "ticket_medio",
                "gasto_medio_cliente"
            ]
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

    # 6. INFORMAR OS ARQUIVOS EXPORTADOS
    print("\n=== RF09 - EXPORTAÇÃO CONCLUÍDA ===")

    print(f"Métricas mensais: {caminho_metricas}")
    print(f"Segmentação de clientes: {caminho_segmentacao}")
    print(f"Estatísticas gerais: {caminho_estatisticas}")

    return {
        "metricas_por_mes": caminho_metricas,
        "segmentacao_clientes": caminho_segmentacao,
        "estatisticas_gerais": caminho_estatisticas
    }


# ============================================================
# RF10 - INTEGRAÇÃO E EXECUÇÃO COMPLETA DO PROJETO
# ============================================================

class AnalisadorDeVendas:
    """
    Coordena a execução ponta a ponta do SalesInsight PY,
    integrando as funções existentes de RF01 a RF09.
    """

    def __init__(self):
        # Caminhos absolutos baseados na pasta deste arquivo.
        self.pasta_projeto = os.path.dirname(os.path.abspath(__file__))
        self.caminho_csv = os.path.join(
            self.pasta_projeto,
            "vendas.csv"
        )
        self.pasta_outputs = os.path.join(
            self.pasta_projeto,
            "outputs"
        )

        # DataFrames utilizados durante a execução.
        self.df_bruto = None
        self.df_limpo = None
        self.df_rf04 = None
        self.df_rf08 = None
        self.df_extra2 = None

        # Resultados das análises.
        self.relatorio_limpeza = None
        self.metricas = None
        self.clientes_segmentados = None
        self.estatisticas = None
        self.tabela_mes_categoria = None
        self.vendas_por_dia = None
        self.maior_fluxo = None
        self.menor_fluxo = None

    def garantir_dataset(self):
        """Gera o CSV somente se ele ainda não existir."""

        if not os.path.exists(self.caminho_csv):
            print("\n=== RF01 - GERAÇÃO DO DATASET ===")

            # Gera os dados sem salvar em um caminho relativo.
            df_gerado = gerar_dataset_vendas()

            # Salva uma única vez no caminho definido pelo RF10.
            df_gerado.to_csv(
                self.caminho_csv,
                index=False
            )

            print(
                f"Dataset gerado com {len(df_gerado)} registros."
            )
            print(
                f"Arquivo salvo em: {self.caminho_csv}"
            )
            print(df_gerado.head())

        else:
            print(
                "\nDataset existente encontrado: "
                f"{self.caminho_csv}"
            )

    def carregar_dataset(self):
        """Garante a existência do CSV e carrega os dados brutos."""

        print("\n=== CARREGAMENTO DO DATASET ===")

        self.garantir_dataset()

        self.df_bruto = pd.read_csv(self.caminho_csv)

        print("Dataset carregado com sucesso.")
        print(f"Total de registros: {len(self.df_bruto)}")

        inspecionar_dados(self.df_bruto)

    def executar_limpeza(self):
        """Executa a limpeza antes de qualquer transformação."""

        print("\n=== RF03 - LIMPEZA DOS DADOS ===")

        (
            self.df_limpo,
            self.relatorio_limpeza
        ) = tratar_dados(self.df_bruto)

    def executar_transformacoes(self):
        """Executa as transformações RF04 e RF08."""

        print("\n=== RF04 - TRANSFORMAÇÕES ===")

        self.df_rf04 = criar_colunas_derivadas(
            self.df_limpo
        )

        exibir_resultados_rf04(self.df_rf04)

        print("\n=== RF08 - FUNÇÃO DE ORDEM SUPERIOR ===")

        self.df_rf08 = testar_funcao_ordem_superior(
            self.df_rf04
        )

        exibir_teste_funcao_ordem_superior(
            self.df_rf08
        )

    def executar_analises(self):
        """Executa métricas, análises e segmentações."""

        print("\n=== RF05 - MÉTRICAS AGREGADAS ===")

        self.metricas = calcular_metricas(self.df_rf04)
        exibir_metricas(self.metricas)

        print("\n=== B03 - TABELA MÊS X CATEGORIA ===")

        self.tabela_mes_categoria = criar_tabela_mes_categoria(
            self.df_rf04
        )

        exibir_tabela_mes_categoria(
            self.tabela_mes_categoria
        )

        print("\n=== ANÁLISE DE VENDAS POR DIA DA SEMANA ===")

        (
            self.df_extra2,
            self.vendas_por_dia,
            self.maior_fluxo,
            self.menor_fluxo
        ) = analisar_vendas_por_dia_semana(self.df_rf04)

        exibir_analise_vendas_por_dia_semana(
            self.df_extra2,
            self.vendas_por_dia,
            self.maior_fluxo,
            self.menor_fluxo
        )

        print("\n=== RF06 - SEGMENTAÇÃO DE CLIENTES ===")

        self.clientes_segmentados = segmentar_clientes(
            self.df_rf04
        )

        exibir_segmentacao_clientes(
            self.clientes_segmentados
        )

    def executar_visualizacoes(self):
        """Gera os gráficos RF07, bônus e extras."""

        print("\n=== RF07 - VISUALIZAÇÕES ===")

        criar_grafico_receita_por_mes(self.metricas)
        criar_grafico_top_produtos(self.metricas)
        criar_grafico_quantidade_vs_receita(self.df_rf04)
        criar_grafico_receita_por_regiao(self.metricas)

        criar_painel_resumo(
            self.metricas,
            self.df_rf04
        )

        print("\n=== GRÁFICO BÔNUS B03 ===")

        criar_grafico_receita_por_mes_categoria(
            self.tabela_mes_categoria
        )

        print("\n=== GRÁFICOS EXTRAS ===")

        criar_grafico_vendas_por_dia_semana(
            self.vendas_por_dia
        )

        criar_grafico_receita_categoria_produtos(
            self.metricas,
            self.df_rf04
        )

        criar_grafico_receita_por_trimestre_top5(
            self.df_rf04,
            self.metricas
        )

        criar_grafico_receita_segmento_categoria(
            self.df_rf04,
            self.clientes_segmentados
        )

        criar_grafico_clientes_regiao_segmento(
            self.df_rf04,
            self.clientes_segmentados
        )

        print("\n=== MAPA DE CALOR B04 ===")

        criar_mapa_calor_receita_produto_categoria(
            self.df_rf04
        )

    def exibir_resumo_e_conclusao(self):
        """Apresenta o resumo com as métricas calculadas."""

        print("\n" + "=" * 60)
        print("SALESINSIGHT PY - RESUMO E CONCLUSÃO")
        print("=" * 60)

        # Produto com maior receita.
        top_produto = self.metricas["top_produtos"].iloc[0]

        print(
            f"\nProduto de maior receita no Top 5: "
            f"{top_produto['produto']} "
            f"(R$ {top_produto['receita_total']:,.2f})"
        )

        # Categoria com maior receita.
        top_categoria = self.metricas["por_categoria"].iloc[0]

        print(
            f"Categoria de maior receita: "
            f"{top_categoria['categoria']} "
            f"(R$ {top_categoria['receita_total']:,.2f})"
        )

        # Região com maior receita.
        top_regiao = self.metricas["por_regiao"].iloc[0]

        print(
            f"Região de maior receita: "
            f"{top_regiao['regiao']} "
            f"(R$ {top_regiao['receita_total']:,.2f})"
        )

        # Mês com maior receita.
        dados_mensais = self.metricas["por_mes"]

        top_mes = dados_mensais.loc[
            dados_mensais["receita_total"].idxmax()
        ]

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

        nome_mes = meses[int(top_mes["mes"])]

        print(
            f"Mês de maior receita: {nome_mes} "
            f"(R$ {top_mes['receita_total']:,.2f})"
        )

        print(
            f"\nRegistros válidos após a limpeza: "
            f"{len(self.df_limpo)}"
        )

        print(
            "\nConclusão: as métricas e visualizações acima "
            "permitem identificar os produtos, as categorias, "
            "as regiões e os períodos de maior receita. "
            "Esses resultados podem apoiar a análise do "
            "desempenho comercial."
        )

    def executar_exportacao(self):
        """Prepara estatísticas e executa a exportação RF09 uma vez."""

        print("\n=== RF09 - EXPORTAÇÃO DOS RESULTADOS ===")

        self.estatisticas = preparar_estatisticas_gerais(
            self.metricas,
            self.df_rf04,
            self.clientes_segmentados
        )

        exportar_resultados(
            self.metricas,
            self.clientes_segmentados,
            self.estatisticas
        )

    def executar(self):
        """Executa o fluxo completo na ordem definida pelo RF10."""

        print("=" * 60)
        print("SALESINSIGHT PY - INÍCIO DA EXECUÇÃO")
        print("=" * 60)

        self.carregar_dataset()
        self.executar_limpeza()
        self.executar_transformacoes()
        self.executar_analises()
        self.executar_visualizacoes()
        self.exibir_resumo_e_conclusao()
        self.executar_exportacao()

        print("\n" + "=" * 60)
        print("SALESINSIGHT PY - EXECUÇÃO CONCLUÍDA")
        print("=" * 60)

        print(
            "\nArquivos CSV e JSON exportados para a pasta outputs."
        )
        print("Gráficos salvos na pasta outputs/graficos.")

        return self


# ============================================================
# PONTO DE ENTRADA DO PROGRAMA - RF10
# ============================================================

def main():
    """Ponto de entrada principal do SalesInsight PY."""

    analisador = AnalisadorDeVendas()
    analisador.executar()


if __name__ == "__main__":
    main()