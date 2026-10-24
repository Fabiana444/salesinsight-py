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


# B03 - Tabela cruzada mês x categoria

# B03 - Tabela cruzada mês x categoria

# Agrupar a receita total por mês e categoria
receita_mes_categoria = df_rf04.groupby(["mes", "mes_nome", "categoria"])["receita_total"].sum().reset_index()

# Criar a tabela cruzada
tabela_mes_categoria = receita_mes_categoria.pivot(
    index=["mes", "mes_nome"],
    columns="categoria",
    values="receita_total"
)

# Exibir a tabela cruzada
print("=== B03 - RECEITA TOTAL POR MÊS E CATEGORIA ===")
print(tabela_mes_categoria)