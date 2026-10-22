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
