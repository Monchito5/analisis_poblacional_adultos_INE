# abstract.py
import pandas as pd
from pathlib import Path
from src.config.settings import ABSTRACT_DIR, PATHS

# Configuración de regiones unificada
REGION_CONFIG_2015 = {
    "Jalisco": {
        "entidad": 14
    },
    "ZMG": {
        "distrito_cod": [7, 8, 9, 11, 12, 13, 14, 15, 16]
    },
    "GDL": {
        "distrito_cod": [8, 9, 11, 14]
    }
}

# Configuración específica para 2020 (usa distritos electorales)
REGION_CONFIG_2020 = {
    "Jalisco": {
        "distrito_cod": None  # Todo el estado
    },
    "ZMG": {
        "distrito_cod": [7, 8, 9, 11, 12, 13, 14, 15, 16]
    },
    "GDL": {
        "distrito_cod": [8, 9, 11, 14]
    }
}

REGION_CONFIG_2025 = {
    "Jalisco": {
        "clave_entidad": 14
    },
    "ZMG": {
        "clave_distrito": [7, 8, 9, 11, 12, 13, 14, 15, 16]
    },
    "GDL": {
        "clave_distrito": [8, 9, 11, 14]
    }
}

def aplicar_filtros(df, filtros):
    """Aplica filtros a un DataFrame de manera flexible"""
    sub = df.copy()
    for col, val in filtros.items():
        if val is None:
            continue  # No aplicar filtro
        elif isinstance(val, list):
            sub = sub[sub[col].isin(val)]
        else:
            sub = sub[sub[col] == val]
    return sub

def generar_resumen_2015():
    """Genera resumen para datos del censo 2015"""
    # Cargar datos preparados usando ruta de settings
    df = pd.read_csv(PATHS["eige_2015"]["prepared"])

    rows = []
    for region, filtros in REGION_CONFIG_2015.items():
        # Aplicar filtros de región
        sub = aplicar_filtros(df, filtros)

        # Calcular población total y porcentajes de hombres y mujeres
        # Mayores de 18 años
        pob_total = sub["pob_total"].sum()
        hombres_18 = sub["hombres_18+"].sum()
        mujeres_18 = sub["mujeres_18+"].sum()
        porcentaje_hombres = (hombres_18 / pob_total) * 100
        porcentaje_mujeres = (mujeres_18 / pob_total) * 100

        rows.append({
            "REGIÓN": region,
            "AÑO": 2015,
            "POB_TOT": pob_total,
            "HOMBRES_18+": hombres_18,
            "MUJERES_18+": mujeres_18,
            "PORCENTAJE_HOMBRES": round(porcentaje_hombres, 1),
            "PORCENTAJE_MUJERES": round(porcentaje_mujeres, 1)
        })

    return pd.DataFrame(rows)

def generar_resumen_2020():
    """Genera resumen para datos del INE 2020"""
    # Cargar datos preparados usando ruta de settings
    df = pd.read_csv(PATHS["ine_2020"]["prepared"])
    
    # Filtrar solo Jalisco (entidad 14)
    df = df[df["entidad"] == 14]
    
    rows = []
    for region, filtros in REGION_CONFIG_2020.items():
        # Aplicar filtros de región
        sub = aplicar_filtros(df, filtros)
        
        # Sumar poblaciones
        pop_total = sub["p_18ymas"].sum()
        pop_hombres = sub["hombres_18+"].sum()
        pop_mujeres = sub["mujeres_18+"].sum()
        
        porcentaje_hombres = (pop_hombres / pop_total) * 100
        porcentaje_mujeres = (pop_mujeres / pop_total) * 100
        
        rows.append({
            "REGIÓN": region,
            "AÑO": 2020,
            "POB_TOT": int(pop_total),
            "HOMBRES_18+": int(pop_hombres),
            "MUJERES_18+": int(pop_mujeres),
            "PORCENTAJE_HOMBRES": round(porcentaje_hombres, 1),
            "PORCENTAJE_MUJERES": round(porcentaje_mujeres, 1)
        })
    
    return pd.DataFrame(rows)

def generar_resumen_2025():
    """Genera resumen para datos del INE 2025"""
    # Cargar datos preparados usando ruta de settings
    df = pd.read_csv(PATHS["ine_2025"]["prepared"], encoding="latin1")
    
    rows = []
    for region, filtros in REGION_CONFIG_2025.items():
        # Aplicar filtros de región
        sub = aplicar_filtros(df, filtros)
        
        # Calcular poblaciones
        hombres = sub["padron_hombres"].sum()
        mujeres = sub["padron_mujeres"].sum()
        
        pop_total = hombres + mujeres
        porcentaje_hombres = (hombres / pop_total) * 100
        porcentaje_mujeres = (mujeres / pop_total) * 100
        
        rows.append({
            "REGIÓN": region,
            "AÑO": 2025,
            "POB_TOT": int(pop_total),
            "HOMBRES_18+": int(hombres),
            "MUJERES_18+": int(mujeres),
            "PORCENTAJE_HOMBRES": round(porcentaje_hombres, 1),
            "PORCENTAJE_MUJERES": round(porcentaje_mujeres, 1)
        })

    return pd.DataFrame(rows)

def main():
    """Función principal para generar el resumen consolidado"""
    # Crear directorio si no existe
    ABSTRACT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("🔍 Generando resumen para 2015...")
    resumen_2015 = generar_resumen_2015()
    
    print("🔍 Generando resumen para 2020...")
    resumen_2020 = generar_resumen_2020()
    
    print("🔍 Generando resumen para 2025...")
    resumen_2025 = generar_resumen_2025()
    
    # Combinar todos los resultados
    resumen_final = pd.concat(
        [resumen_2015, resumen_2020, resumen_2025],
        ignore_index=True
    )
    
    # Guardar resultados
    output_path = ABSTRACT_DIR / "resumen_final.csv"
    resumen_final.to_csv(output_path, index=False)
    
    print("✅ Resumen final generado:")
    print(resumen_final)
    print(f"📁 Guardado en: {output_path}")

if __name__ == "__main__":
    main()
