# Análisis exploratorio
import pandas as pd
import json
from pathlib import Path
from src.config.settings import PATHS, ABSTRACT_DIR, OUTPUT_DIR

# Mapeo de códigos a nombres de distritos
DISTRITO_MAP = {
    1: "TEQUILA",
    2: "LAGOS DE MORENO",
    3: "TEPATITLÁN DE MORELOS",
    4: "ZAPOPAN",
    5: "PUERTO VALLARTA",
    6: "ZAPOPAN",
    7: "TONALÁ",
    8: "GUADALAJARA",
    9: "GUADALAJARA",
    10: "ZAPOPAN",
    11: "GUADALAJARA",
    12: "TLAJOMULCO DE ZUÑIGA",
    13: "SAN PEDRO TLAQUEPAQUE",
    14: "TLAJOMULCO DE ZUÑIGA",
    15: "LA BARCA",
    16: "SAN PEDRO TLAQUEPAQUE",
    17: "JOCOTEPEC",
    18: "AUTLÁN DE NAVARRO",
    19: "ZAPOTLÁN",
    20: "TONALÁ"
}

# Agrupación de códigos por distrito real
DISTRITO_GROUP = {
    "TEQUILA": [1],
    "LAGOS DE MORENO": [2],
    "TEPATITLÁN DE MORELOS": [3],
    "ZAPOPAN": [4, 6, 10],
    "PUERTO VALLARTA": [5],
    "TONALÁ": [7, 20],
    "GUADALAJARA": [8, 9, 11],
    "TLAJOMULCO DE ZUÑIGA": [12, 14],
    "SAN PEDRO TLAQUEPAQUE": [13, 16],
    "LA BARCA": [15],
    "JOCOTEPEC": [17],
    "AUTLÁN DE NAVARRO": [18],
    "ZAPOTLÁN": [19]
}

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

def add_distrito_name(df, code_col="distrito_cod"):
    """Añade columna con nombre del distrito"""
    df["distrito_nombre"] = df[code_col].map(DISTRITO_MAP)
    return df

def group_by_distrito_name(df, code_col="distrito_cod"):
    """Agrupa por nombre de distrito (combinando códigos)"""
    # Crear mapeo inverso para agrupación
    inverse_map = {}
    for distrito, codigos in DISTRITO_GROUP.items():
        for codigo in codigos:
            inverse_map[codigo] = distrito
    
    df["distrito_nombre"] = df[code_col].map(inverse_map)
    return df

def explorer_2015():
    """Análisis exploratorio para EIGE 2015 - ACTUALIZADO"""
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

    # Añadir nombres y agrupar distritos
    df = add_distrito_name(df)
    df = group_by_distrito_name(df)
    
    # 1. Población adulta por nombre de distrito (agrupado)
    adult_data = df.groupby("distrito_nombre", as_index=False).agg({
        "hombres_18+": "sum",
        "mujeres_18+": "sum"
    })
    adult_data["total_adultos"] = adult_data["hombres_18+"] + adult_data["mujeres_18+"]
    adult_data.to_csv(ABSTRACT_DIR / "poblacion_adulta_2015.csv", index=False)
    print("✔️ Población adulta por distrito REAL guardada")

    # 2. Grupos de edad absolutos para Jalisco (convertir % a valores reales)
    age_cols = [c for c in df.columns if c.startswith("porc_")]
    jalisco_total = df["pob_total"].sum()
    
    age_data = []
    for col in age_cols:
        grupo = col.replace("porc_", "")
        poblacion_grupo = (df[col].mean() / 100) * jalisco_total
        age_data.append({"grupo_edad": grupo, "poblacion": round(poblacion_grupo)})
    
    pd.DataFrame(age_data).to_csv(ABSTRACT_DIR / "distribucion_edad_absoluta_jalisco_2015.csv", index=False)
    print("✔️ Distribución edad absoluta (Jalisco) guardada")

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
    """Análisis exploratorio para INE 2020 - ACTUALIZADO"""
    df = pd.read_csv(PATHS["ine_2020"]["prepared"])
    print(f"🔍 Cargando datos 2020 ({len(df)} filas)")
    validate_columns(df, {"entidad", "distrito_cod", "hombres_18+", "mujeres_18+", "p_0a17", "p_18ymas"}, "ine_2020")

    # Añadir nombres y agrupar distritos
    df = add_distrito_name(df)
    df = group_by_distrito_name(df)

    # 1. Población adulta por nombre de distrito (agrupado)
    df["pob_total"] = df["p_0a17"] + df["p_18ymas"]
    adult_data = df.groupby("distrito_nombre", as_index=False).agg({
        "hombres_18+": "sum",
        "mujeres_18+": "sum",
        "p_18ymas": "sum"
    })
    adult_data.rename(columns={"p_18ymas": "total_adultos"}, inplace=True)
    adult_data.to_csv(ABSTRACT_DIR / "poblacion_adulta_2020.csv", index=False)
    print("✔️ Población adulta por nombre de distrito guardada")

    # 2. Resumen Jalisco
    jalisco_2020 = {
        "entidad": 14,
        "hombres_18+": df["hombres_18+"].sum(),
        "mujeres_18+": df["mujeres_18+"].sum(),
        "total_adultos": df["p_18ymas"].sum()
    }
    pd.DataFrame([jalisco_2020]).to_csv(ABSTRACT_DIR / "resumen_jalisco_2020.csv", index=False)
    print("✔️ Resumen Jalisco guardado en resumen_jalisco_2020.csv")

    # 1. Distribución por sexo en 18+ (frecuencia y %)
    calculate_distribution(df, "hombres_18+", "sexo_ine_2020")
    calculate_distribution(df, "mujeres_18+", "sexo_ine_2020_mujeres")

    # 2. Distribución por grupo de edad (%)
    calculate_distribution(df, "p_0a17", "edad_0a17_ine_2020")
    calculate_distribution(df, "p_18ymas", "edad_18ymas_ine_2020")

    # 3. Metadata
    save_metadata(df, "ine2020")

def explorer_2025():
    """Análisis exploratorio para INE 2025 - ACTUALIZADO"""
    df = pd.read_csv(PATHS["ine_2025"]["prepared"], encoding="latin1")
    print(f"🔍 Cargando datos 2025 ({len(df)} filas)")
    required = {
        "clave_distrito", "clave_municipio", "nombre_municipio",
        "padron_electoral", "lista_nominal",
        "lista_hombres", "lista_mujeres",
        "padron_hombres", "padron_mujeres"
    }
    validate_columns(df, required, "ine_2025")

    # Añadir nombres de distrito usando clave_distrito
    df = add_distrito_name(df.copy(), code_col="clave_distrito")
    df = group_by_distrito_name(df.copy(), code_col="clave_distrito")

    # 1. Agrupar por nombre de distrito
    distrito_data = df.groupby("distrito_nombre", as_index=False).agg({
        "padron_hombres": "sum",
        "padron_mujeres": "sum",
        "padron_electoral": "sum"
    })
    distrito_data.rename(columns={
        "padron_hombres": "hombres_18+",
        "padron_mujeres": "mujeres_18+",
        "padron_electoral": "total_adultos"
    }, inplace=True)
    distrito_data.to_csv(ABSTRACT_DIR / "poblacion_adulta_distrito_2025.csv", index=False)

    # 2. Agrupar por municipio (para ZMG)
    municipio_data = df.groupby(["clave_municipio", "nombre_municipio"], as_index=False).agg({
        "padron_hombres": "sum",
        "padron_mujeres": "sum",
        "padron_electoral": "sum"
    })
    municipio_data.rename(columns={
        "padron_hombres": "hombres_18+",
        "padron_mujeres": "mujeres_18+",
        "padron_electoral": "total_adultos"
    }, inplace=True)
    municipio_data.to_csv(ABSTRACT_DIR / "poblacion_adulta_municipio_2025.csv", index=False)
    print("✔️ Datos adultos por distrito/municipio guardados")

    # 1. Distribución general de padron vs lista
    calculate_distribution(df, "padron_electoral", "conteo_general_ine_2025")
    calculate_distribution(df, "lista_nominal", "lista_general_ine_2025")

    # 2. Distribución por sexo en lista nominal
    calculate_distribution(df, "lista_hombres", "lista_hombres_ine_2025")
    calculate_distribution(df, "lista_mujeres", "lista_mujeres_ine_2025")

    # 3. Distribución por sexo en padrón electoral
    calculate_distribution(df, "padron_hombres", "padron_hombres_ine_2025")
    calculate_distribution(df, "padron_mujeres", "padron_mujeres_ine_2025")

    # 4. Metadata
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