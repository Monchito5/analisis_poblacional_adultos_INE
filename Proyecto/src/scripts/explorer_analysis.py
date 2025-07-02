# Análisis exploratorio

import pandas as pd
import json

from src.config.settings import PATHS, ABSTRACT_DIR, OUTPUT_DIR
from pathlib import Path

def save_metadata(df, nombre_archivo):
    metadata = {
        "filas": int(df.shape[0]),
        "columnas": int(df.shape[1]),
        "columnas_nombres": list(df.columns)
    }
    with open(ABSTRACT_DIR / f"{nombre_archivo}_meta.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✔️ Metadata guardada: {nombre_archivo}_meta.json")

def validate_columns(df, required_columns, dataset_name):
    faltantes = required_columns.difference(df.columns)
    if faltantes:
        raise ValueError(f"❌ Columnas faltantes en {dataset_name}: {faltantes}")
    print(f"✔️ Columnas válidas para {dataset_name}")

def calculate_distribution(df, column, output_name):
    counts = (
        df[column]
          .value_counts(normalize=True)
          .rename_axis(column)
          .reset_index(name="frecuencia")
    )
    counts["frecuencia_%"] = (counts["frecuencia"] * 100).round(2)
    counts.to_csv(ABSTRACT_DIR / f"{output_name}.csv", index=False)
    print(f"✔️ Distribución de {column} guardada en {output_name}.csv")

def explorer_2015():
    """Análisis exploratorio para EIGE 2015"""
    path_raw = PATHS["eige_2015"]["prepared"]
    df = pd.read_csv(path_raw)
    print(f"🔍 Cargando datos 2015 desde {path_raw.name} ({len(df)} filas)")

    # 1. Validar columnas
    required_cols = {
        "entidad", "distrito_cod", "pob_total",
        "hombres_18+", "mujeres_18+",
        "porc_0a9", "porc_10a19", "porc_20a29",
        "porc_30a39", "porc_40a49", "porc_50a59",
        "porc_60ymas", "porc_edadne"
    }
    validate_columns(df, required_cols, "eige_2015")

    # 2. Estadísticos descriptivos globales
    desc = df.describe(percentiles=[.25, .5, .75]).T
    desc.to_csv(ABSTRACT_DIR / "resumen_eige2015.csv")
    print("✔️ Estadísticos descriptivos globales guardados en resumen_eige2015.csv")

    # 3. Distribución población por distrito
    calculate_distribution(df, "distrito_cod", "distribucion_distrito_eige2015")

    # 4. Distribución por grupos de edad (promedio %)
    grupos = (
        df[[
            "porc_0a9", "porc_10a19", "porc_20a29",
            "porc_30a39", "porc_40a49", "porc_50a59",
            "porc_60ymas", "porc_edadne"
        ]]
        .mean()
        .reset_index()
        .rename(columns={"index": "grupo_edad", 0: "porcentaje_promedio"})
    )
    grupos["porcentaje_promedio"] = grupos["porcentaje_promedio"].round(2)
    grupos.to_csv(ABSTRACT_DIR / "distribucion_edad_eige2015.csv", index=False)
    print("✔️ Distribución promedio de edad guardada en distribucion_edad_eige2015.csv")

    # 5. Correlaciones
    corr_cols = [
        "pob_total", "hombres_18+", "mujeres_18+",
        "porc_20a29", "porc_30a39", "porc_40a49", "porc_50a59"
    ]
    corr = df[corr_cols].corr().round(2)
    corr.to_csv(ABSTRACT_DIR / "correlacion_eige2015.csv")
    print("✔️ Matriz de correlaciones guardada en correlacion_eige2015.csv")

    # 6. Metadata
    save_metadata(df, "eige2015")

def explorer_2020():
    df = pd.read_csv(PATHS["ine_2020"]["prepared"])
    print(f"🔍 Cargando datos 2020 ({len(df)} filas)")
    validate_columns(df, {"hombres_18+", "mujeres_18+", "p_0a17", "p_18ymas"}, "ine_2020")

    calculate_distribution(df, "hombres_18+", "sexo_ine_2020")
    calculate_distribution(df, "p_0a17", "edad_ine_2020")
    save_metadata(df, "ine2020")

def explorer_2025():
    df = pd.read_csv(PATHS["ine_2025"]["prepared"], encoding="latin1")
    print(f"🔍 Cargando datos 2025 ({len(df)} filas)")
    required = {
        "padron_electoral", "lista_nominal",
        "lista_hombres", "lista_mujeres",
        "padron_hombres", "padron_mujeres"
    }
    validate_columns(df, required, "ine_2025")

    calculate_distribution(df, "padron_electoral", "conteo_poblacional_ine_2025")
    calculate_distribution(df, "lista_hombres", "lista_sexo_ine_2025")
    calculate_distribution(df, "padron_hombres", "padron_sexo_ine_2025")
    save_metadata(df, "ine2025")

def main():
    # Asegurar directorios
    for folder in (ABSTRACT_DIR, OUTPUT_DIR):
        Path(folder).mkdir(parents=True, exist_ok=True)

    print("🔍 Explorando datos EIGE 2015...")
    explorer_2015()
    print("🔍 Explorando datos INE 2020...")
    explorer_2020()
    print("🔍 Explorando datos INE 2025...")
    explorer_2025()
    print("✅ Exploración completada. CSVs en:", ABSTRACT_DIR)

if __name__ == "__main__":
    main()
