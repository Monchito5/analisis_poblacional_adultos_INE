# Limpieza y preparación unificada de datasets

import argparse
import pandas as pd
import re
from src.config.settings import PATHS

def clean_eige_2015(raw_path, prepared_path):
    """Limpieza y preparación de datos Encuesta Intercensal Geoelectoral 2015"""

    # Lista en minúsculas de los indicadores que realmente necesitamos
    desired = {
        "cve_ent", "cve_distrito",
        "ind_806", "ind_807", "ind_808", "ind_810",
        "ind_818", "ind_819", "ind_820", "ind_821",
        "ind_822", "ind_823", "ind_824", "ind_825"
    }

    # Cargar sólo columnas cuya versión minúsculas (sin espacios) esté en desired
    df = pd.read_csv(
        raw_path,
        usecols=lambda col: col.strip().lower() in desired,
        encoding="utf-8-sig"
    )

    # Normalizar nombres a minúsculas y sin espacios
    df.columns = df.columns.str.strip().str.lower()

    # Renombrar según diccionario mnemónico
    df = df.rename(columns={
        "cve_ent":        "entidad",
        "cve_distrito":   "distrito_cod",
        "ind_806":        "pob_total",
        "ind_807":        "porc_18ymas",
        "ind_808":        "hombres_18+",
        "ind_810":        "mujeres_18+",
        "ind_818":        "porc_0a9",
        "ind_819":        "porc_10a19",
        "ind_820":        "porc_20a29",
        "ind_821":        "porc_30a39",
        "ind_822":        "porc_40a49",
        "ind_823":        "porc_50a59",
        "ind_824":        "porc_60ymas",
        "ind_825":        "porc_edadne"
    })

    # Eliminar distritos sin población
    df = df[df["distrito_cod"] != 0]
    # Filtrar solo Jalisco (entidad = 14)
    df = df[df["entidad"] == 14]

    # Guardar dataset preparado
    df.to_csv(prepared_path, index=False)
    print(f"✅ eige_2015 preparado en {prepared_path}")

def clean_ine_2020(raw_path, prepared_path):
    cfg = {
        "usecols": [
            "ENTIDAD", "DISTRITO", "P_0A17",
            "P_18YMAS", "P_18YMAS_F", "P_18YMAS_M",
            "P15YM_AN", "P15YM_SE"
        ],
        "col_map": {
            "ENTIDAD": "entidad",
            "DISTRITO": "distrito_cod",
            "P_0A17": "p_0a17",
            "P_18YMAS": "p_18ymas",
            "P_18YMAS_M": "hombres_18+",
            "P_18YMAS_F": "mujeres_18+",
            "P15YM_AN": "p15ym_an",
            "P15YM_SE": "p15ym_se"
        }
    }
    df = pd.read_csv(raw_path, usecols=cfg["usecols"], encoding="utf-8-sig")
    df = df.rename(columns=cfg["col_map"])
    df.columns = df.columns.str.lower()
    df = df[df["entidad"] == 14]
    df["tiene_ine"] = (
        df["p_18ymas"] - (df["p15ym_an"] + df["p15ym_se"] + df["p_0a17"])
    )
    cols_finales = [
        "entidad", "distrito_cod", "tiene_ine",
        "p_0a17", "p_18ymas", "hombres_18+", "mujeres_18+"
    ]
    df[cols_finales].to_csv(prepared_path, index=False)
    print(f"✅ ine_2020 preparado en {prepared_path}")


def clean_ine_2025(raw_path, prepared_path):
    df = pd.read_csv(raw_path, encoding="latin1")
    # normalizar nombres
    df.columns = (
        df.columns
        .str.replace('"', '')
        .str.strip()
        .str.replace(r'\s+', '_', regex=True)
        .str.lower()
    )
    # filtrar Jalisco
    df = df[df['clave_entidad'] == 14].copy()
    # limpiar espacios en object
    df = df.apply(lambda s: s.str.strip() if s.dtype == "object" else s)
    # cabecera distrital
    df['cabecera_distrital'] = df['cabecera_distrital'].str.replace(r'\s+', ' ', regex=True)
    df.to_csv(prepared_path, index=False, encoding="latin1")
    print(f"✅ ine_2025 preparado en {prepared_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Limpieza y preparación unificada de datasets"
    )
    parser.add_argument(
        "--dataset",
        required=True,
        choices=PATHS.keys(),
        help="Nombre del dataset a procesar (p.ej. eige_2015)"
    )
    args = parser.parse_args()

    paths = PATHS[args.dataset]
    raw_path      = paths["raw"]
    prepared_path = paths["prepared"]

    # despacho según dataset
    dispatch_map = {
        "eige_2015": clean_eige_2015,
        "ine_2020": clean_ine_2020,
        "ine_2025": clean_ine_2025
    }

    try:
        dispatch_map[args.dataset](raw_path, prepared_path)
    except KeyError:
        raise ValueError(f"Dataset desconocido: {args.dataset}")

if __name__ == "__main__":
    main()

