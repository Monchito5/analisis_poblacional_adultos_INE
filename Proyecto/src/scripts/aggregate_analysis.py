# Proyecto Minería de Datos — Proyección 2015–2035

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from scipy import stats

from src.config.settings import ABSTRACT_DIR, STAT_GRAPHS

# --- 1. Cargar y limpiar el maestro ---
def load_and_clean_master(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Eliminar filas con NA en columnas críticas
    df = df.dropna(subset=["POB_TOT", "HOMBRES_18+", "MUJERES_18+"]).copy()
    # Z-score para POB_TOT y filtrar outliers (>3σ)
    z = np.abs(stats.zscore(df["POB_TOT"]))
    df = df[z < 3]
    # Asegurar tipo de REGIÓN
    df["REGIÓN"] = df["REGIÓN"].astype(str)
    return df.reset_index(drop=True)

# --- 2. Construir serie histórica 2015–2025 ---
def build_historical(master: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for region, grp in master.groupby("REGIÓN"):
        # Reindexar años 2015–2025
        grp = grp.sort_values("AÑO").set_index("AÑO")
        full = grp.reindex(range(2015, 2026))
        # Interpolar columnas numéricas
        num_cols = ["POB_TOT", "HOMBRES_18+", "MUJERES_18+"]
        full[num_cols] = full[num_cols].interpolate(method="linear")
        # Rellenar región y año
        full["REGIÓN"] = region
        full = full.reset_index()
        # Redondear población a entero
        full[num_cols] = full[num_cols].round().astype(int)
        frames.append(full)
    return pd.concat(frames, ignore_index=True)

# --- 3. Proyección hasta 2035 ---
def project_to_2035(hist_df: pd.DataFrame) -> pd.DataFrame:
    projections = []
    metrics = ["POB_TOT", "HOMBRES_18+", "MUJERES_18+"]
    for region, grp in hist_df.groupby("REGIÓN"):
        X = grp[["AÑO"]].values
        future_years = np.arange(2026, 2036).reshape(-1, 1)
        df_pred = pd.DataFrame({"AÑO": future_years.flatten()})
        for m in metrics:
            y = grp[m].values
            model = LinearRegression().fit(X, y)
            pred = model.predict(future_years).round().astype(int)
            df_pred[m] = pred
            r2 = r2_score(y, model.predict(X))
            mse = mean_squared_error(y, model.predict(X))
            print(f"{region} | {m}: R²={r2:.3f}, MSE={mse:.0f}")
        df_pred["REGIÓN"] = region
        projections.append(df_pred)
    return pd.concat(projections, ignore_index=True)

# --- 4. Clasificación de mayoría de género ---
def logistic_majority_gender(df: pd.DataFrame):
    df = df.copy()
    df["MAYORIA_HOMBRES"] = (df["HOMBRES_18+"] > df["MUJERES_18+"]).astype(int)
    X = df[["POB_TOT", "HOMBRES_18+", "MUJERES_18+"]]
    y = df["MAYORIA_HOMBRES"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    clf = LinearRegression()  # Regresión logística no brinda mucho en 0/1
    clf.fit(X_train, y_train)
    y_pred = (clf.predict(X_test) >= 0.5).astype(int)
    acc = (y_pred == y_test).mean()
    print(f"\n🔍 Clasificación mayoría de género — Precisión: {acc:.2f}")

# --- 5. Gráficas descriptivas y series ---
def plot_series(all_df: pd.DataFrame, out_dir: Path):
    sns.set_theme(style="whitegrid")
    metrics = ["POB_TOT", "HOMBRES_18+", "MUJERES_18+"]
    plt.figure(figsize=(12, 6))
    for (reg, met), grp in all_df.melt(
        id_vars=["REGIÓN","AÑO"], 
        value_vars=metrics,
        var_name="Métrica", 
        value_name="Valor"
    ).groupby(["REGIÓN", "Métrica"]):
        label = f"{reg} – {met}"
        plt.plot(grp["AÑO"], grp["Valor"], marker="o", label=label)
    plt.title("Población ≥18 años: Serie Histórica y Proyección (2015–2035)")
    plt.xlabel("Año"); plt.ylabel("Personas")
    plt.legend(fontsize="small", ncol=2)
    plt.tight_layout()
    plt.savefig(out_dir / "serie_historica_proyeccion.png", dpi=300)
    plt.close()
    print("✅ Gráfica de serie histórica guardada.")

# --- Main pipeline ---
def main():
    # Cargar maestro
    master_path = ABSTRACT_DIR / "resumen_final.csv"
    master = load_and_clean_master(master_path)

    # Construir histórico e interpolar
    hist = build_historical(master)

    # Proyectar hacia 2035
    future = project_to_2035(hist)

    # Concatenar todo
    all_data = pd.concat([hist, future], ignore_index=True)

    # Clasificación de mayoría de género
    logistic_majority_gender(all_data)

    # Gráfica de serie histórica + proyección
    plot_series(all_data, STAT_GRAPHS)

if __name__ == "__main__":
    main()
