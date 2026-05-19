# Análise do Catálogo da Netflix (2008–2021)
# Dataset: Netflix Movies and TV Shows
# Fonte:   https://www.kaggle.com/datasets/shivamb/netflix-shows

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import random
import os

# 1. CARREGAMENTO DOS DADOS

CSV_PATH = "netflix_titles.csv"

if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    print(f"✔ CSV carregado: {len(df)} registros")
else:
    print("⚠ 'netflix_titles.csv' nao encontrado — gerando amostra representativa...")

    random.seed(42)
    np.random.seed(42)

    countries_pool = (
        ["United States"] * 50 + ["India"] * 20 + ["United Kingdom"] * 15 +
        ["Japan"] * 12 + ["South Korea"] * 10 + ["Canada"] * 8 +
        ["France"] * 8 + ["Germany"] * 5 + ["Mexico"] * 5 +
        ["Brazil"] * 5 + ["Spain"] * 4 + ["Nigeria"] * 3 + ["Australia"] * 3
    )
    types_pool  = ["Movie"] * 70 + ["TV Show"] * 30
    years_pool  = list(range(2010, 2022))
    genres_pool = [
        "Dramas", "Comedies", "Action & Adventure", "Documentaries",
        "International Movies", "Thrillers", "Horror Movies",
        "Romantic Movies", "Anime Features", "International TV Shows"
    ]
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    records = []
    for i in range(500):
        c      = random.choice(countries_pool)
        t      = random.choice(types_pool)
        y      = random.choice(years_pool)
        g      = random.choice(genres_pool)
        m      = random.choice(months)
        d      = random.randint(1, 28)
        add_yr = random.randint(max(y, 2014), 2021)
        records.append({
            "show_id":      f"s{i+1}",
            "type":         t,
            "country":      c,
            "release_year": y,
            "date_added":   f"{m} {d}, {add_yr}",
            "listed_in":    g,
        })

    df = pd.DataFrame(records)
    print(f"✔ Amostra gerada: {len(df)} registros")

# 2. LIMPEZA E PREPARAÇÃO

df = df.dropna(subset=["country"])
df["date_added"]       = pd.to_datetime(df["date_added"], errors="coerce")
df["ano_adicionado"]   = df["date_added"].dt.year
df["pais_principal"]   = df["country"].str.split(",").str[0].str.strip()
df["genero_principal"] = df["listed_in"].str.split(",").str[0].str.strip()

print(f"\nTotal de títulos : {len(df)}")
print(f"Filmes           : {(df['type']=='Movie').sum()}")
print(f"Séries           : {(df['type']=='TV Show').sum()}")
print(f"Países únicos    : {df['pais_principal'].nunique()}")

# CONFIGURAÇÕES VISUAIS

VERMELHO  = "#E50914"
VERM_ESC  = "#B81D24"
CINZA_ESC = "#221F1F"
CINZA_MED = "#564D4D"
BG        = "#FFFAFA"

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.facecolor":    BG,
    "figure.facecolor":  "white",
    "axes.grid":         True,
    "grid.alpha":        0.35,
    "grid.linestyle":    "--",
})

# GRÁFICO 1 — BARRAS HORIZONTAIS
# Top 10 países com mais títulos no catálogo.
# Tipo adequado para comparar frequências entre categorias discretas.

top_paises = df["pais_principal"].value_counts().head(10).sort_values()
cores_b    = [VERMELHO if c == top_paises.index[-1] else VERM_ESC
              for c in top_paises.index]

fig1, ax1 = plt.subplots(figsize=(10, 6))
bars = ax1.barh(top_paises.index, top_paises.values,
                color=cores_b, edgecolor="white", linewidth=0.6)

for bar, val in zip(bars, top_paises.values):
    ax1.text(val + 0.4, bar.get_y() + bar.get_height() / 2,
             str(val), va="center", fontsize=9,
             color=CINZA_ESC, fontweight="bold")

ax1.set_title("Top 10 Países com Mais Títulos no Catálogo da Netflix",
              fontsize=13, fontweight="bold", pad=14, color=CINZA_ESC)
ax1.set_xlabel("Número de Títulos", fontsize=10)
ax1.set_xlim(0, top_paises.max() * 1.15)

plt.tight_layout()
plt.savefig("grafico1_top10_paises.png", dpi=150, bbox_inches="tight")
plt.show()
print("✔ Gráfico 1 salvo: grafico1_top10_paises.png")

# GRÁFICO 2 — DONUT (Pizza com buraco central)
# Proporção Filmes vs Séries no catálogo.
# Tipo adequado para mostrar composição e partes de um todo.

contagem = df["type"].value_counts()
cores_p  = [VERMELHO, CINZA_MED]

fig2, ax2 = plt.subplots(figsize=(7, 6))
wedges, texts, autotexts = ax2.pie(
    contagem.values,
    labels=contagem.index,
    autopct="%1.1f%%",
    startangle=140,
    colors=cores_p,
    explode=[0.04] * len(contagem),
    wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    textprops={"fontsize": 12},
)
for at in autotexts:
    at.set_fontsize(13)
    at.set_fontweight("bold")
    at.set_color("white")

ax2.text(0, 0, f"{len(df)}\nTítulos", ha="center", va="center",
         fontsize=13, fontweight="bold", color=CINZA_ESC)
ax2.set_title("Proporção de Filmes e Séries no Catálogo da Netflix",
              fontsize=13, fontweight="bold", pad=20, color=CINZA_ESC)

plt.tight_layout()
plt.savefig("grafico2_filmes_vs_series.png", dpi=150, bbox_inches="tight")
plt.show()
print("✔ Gráfico 2 salvo: grafico2_filmes_vs_series.png")

# GRÁFICO 3 — LINHA COM ÁREA
# Quantidade de títulos adicionados ao catálogo por ano.
# Tipo adequado para mostrar tendência e evolução temporal.

por_ano = (df.dropna(subset=["ano_adicionado"])
             .groupby("ano_adicionado")
             .size()
             .reset_index(name="total"))
por_ano = por_ano[por_ano["ano_adicionado"] >= 2014]

fig3, ax3 = plt.subplots(figsize=(10, 5))
ax3.fill_between(por_ano["ano_adicionado"], por_ano["total"],
                 alpha=0.18, color=VERMELHO)
ax3.plot(por_ano["ano_adicionado"], por_ano["total"],
         color=VERMELHO, linewidth=2.5, marker="o", markersize=7)

for _, row in por_ano.iterrows():
    ax3.text(row["ano_adicionado"], row["total"] + 0.5,
             str(int(row["total"])), ha="center", va="bottom",
             fontsize=9, fontweight="bold", color=CINZA_ESC)

ax3.set_title("Crescimento do Catálogo da Netflix por Ano (títulos adicionados)",
              fontsize=13, fontweight="bold", pad=14, color=CINZA_ESC)
ax3.set_xlabel("Ano", fontsize=10)
ax3.set_ylabel("Nº de Títulos Adicionados", fontsize=10)
ax3.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax3.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

plt.tight_layout()
plt.savefig("grafico3_crescimento_anual.png", dpi=150, bbox_inches="tight")
plt.show()
print("✔ Gráfico 3 salvo: grafico3_crescimento_anual.png")

print("\n=== GRÁFICOS GERADOS ===")
print("1. grafico1_top10_paises.png      → Barras horizontais")
print("2. grafico2_filmes_vs_series.png  → Donut / Pizza")
print("3. grafico3_crescimento_anual.png → Linha com área")
