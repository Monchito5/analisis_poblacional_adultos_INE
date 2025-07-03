# Visualización de análisis exploratorio

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from src.config.settings import ABSTRACT_DIR, STAT_GRAPHS

# Asegurar carpeta de destino
STAT_GRAPHS.mkdir(parents=True, exist_ok=True)

# Configuración global mejorada
sns.set_theme(style="whitegrid", context="talk", font_scale=0.9)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
GENDER_PALETTE = {"Hombres": "#3498db", "Mujeres": "#e74c3c"}  # Azul y rojo distintivos

def load_data(filename):
    filepath = ABSTRACT_DIR / f"{filename}.csv"
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"⚠️ Archivo no encontrado: {filepath}")
        return None

def plot_gender_comparison(df, x_col, male_col, female_col, title, filename):
    """Comparativa de población masculina vs femenina"""
    if df is None or df.empty:
        print(f"⛔ Datos vacíos para {filename}")
        return
    
    # Preparar datos
    df_melted = df.melt(
        id_vars=[x_col], 
        value_vars=[male_col, female_col],
        var_name='sexo', 
        value_name='poblacion'
    )
    
    # Traducir etiquetas
    df_melted['sexo'] = df_melted['sexo'].replace({
        male_col: "Hombres",
        female_col: "Mujeres"
    })
    
    # Ordenar por población total
    df_melted = df_melted.sort_values(by='poblacion', ascending=False)
    
    # Crear visualización
    plt.figure(figsize=(14, 8))
    ax = sns.barplot(
        data=df_melted,
        x=x_col,
        y='poblacion',
        hue='sexo',
        palette=GENDER_PALETTE,
        estimator=sum,
        errorbar=None
    )
    
    # Configuración estética
    plt.title(title, fontsize=18, pad=15, fontweight='bold')
    plt.xlabel(x_col.replace('_', ' ').title(), fontsize=14)
    plt.ylabel('Población Adulta', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # Formatear números grandes
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, loc: f"{int(x/1000)}K" if x >= 1000 else f"{int(x)}")
    )
    
    # Añadir etiquetas
    for container in ax.containers:
        labels = [
            f"{int(val/1000)}K" if val >= 10000 else f"{int(val)}" 
            for val in container.datavalues
        ]
        ax.bar_label(
            container, 
            labels=labels,
            label_type='edge',
            padding=5,
            fontsize=10,
            fontweight='bold'
        )
    
    # Leyenda fuera del gráfico
    plt.legend(title='Sexo', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(STAT_GRAPHS / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico guardado: {filename}")

def plot_age_distribution(df, x_col, y_col, title, filename):
    """Distribución por grupos de edad"""
    if df is None or df.empty:
        print(f"⛔ Datos vacíos para {filename}")
        return
    
    # Ordenar por grupo de edad
    if 'grupo_edad' in df.columns:
        age_order = [
            '0a9', '10a19', '20a29', '30a39', 
            '40a49', '50a59', '60ymas', 'edadne'
        ]
        df = df.sort_values(by='grupo_edad', key=lambda x: x.map({v: i for i, v in enumerate(age_order)}))
    
    # Crear visualización
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(
        data=df,
        x=x_col,
        y=y_col,
        color="#2ecc71",  # Verde para datos demográficos
        errorbar=None
    )
    
    # Configuración estética
    plt.title(title, fontsize=18, pad=15, fontweight='bold')
    plt.xlabel('Grupo de Edad', fontsize=14)
    plt.ylabel('Población' if 'poblacion' in y_col else 'Porcentaje', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # Añadir etiquetas
    for container in ax.containers:
        labels = [
            f"{val/1000:.1f}K" if val >= 1000 else f"{int(val)}" 
            for val in container.datavalues
        ]
        ax.bar_label(
            container, 
            labels=labels,
            label_type='edge',
            padding=5,
            fontsize=10,
            fontweight='bold'
        )
    
    plt.tight_layout()
    plt.savefig(STAT_GRAPHS / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico guardado: {filename}")

def plot_top_locations(df, x_col, y_col, title, filename, n=10):
    """Top ubicaciones por población"""
    if df is None or df.empty:
        print(f"⛔ Datos vacíos para {filename}")
        return
    
    # Ordenar y seleccionar top n
    df = df.sort_values(y_col, ascending=False).head(n)
    
    # Crear visualización
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(
        data=df,
        x=x_col,
        y=y_col,
        color="#9b59b6",  # Púrpura para ubicaciones
        errorbar=None
    )
    
    # Configuración estética
    plt.title(title, fontsize=18, pad=15, fontweight='bold')
    plt.xlabel('')
    plt.ylabel('Población Adulta', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # Formatear eje Y
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, loc: f"{int(x/1000)}K")
    )
    
    # Añadir etiquetas
    for container in ax.containers:
        labels = [f"{int(val/1000)}K" for val in container.datavalues]
        ax.bar_label(
            container, 
            labels=labels,
            label_type='edge',
            padding=5,
            fontsize=10,
            fontweight='bold'
        )
    
    plt.tight_layout()
    plt.savefig(STAT_GRAPHS / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico guardado: {filename}")

# ========================================================================
# FUNCIONES ESPECÍFICAS POR AÑO OPTIMIZADAS
# ========================================================================

def graph_2015():
    print("\n📊 Generando gráficas para EIGE 2015...")
    
    # 1. Comparativa hombres vs mujeres por distrito REAL
    df_adultos = load_data("poblacion_adulta_2015")
    if df_adultos is not None:
        plot_gender_comparison(
            df_adultos,
            x_col="distrito_real",  # Actualizado a distrito_real
            male_col="hombres_18+",
            female_col="mujeres_18+",
            title="Población Adulta por Distrito y Sexo - Jalisco 2015",
            filename="adultos_sexo_distrito_2015.png"
        )
    
    # 2. Distribución etaria absoluta en Jalisco
    df_edad = load_data("distribucion_edad_absoluta_jalisco_2015")
    if df_edad is not None:
        plot_age_distribution(
            df_edad,
            x_col="grupo_edad",
            y_col="poblacion",
            title="Distribución Poblacional por Edad - Jalisco 2015",
            filename="distribucion_edad_jalisco_2015.png"
        )
    
    # 3. Top distritos con mayor población adulta (usando distrito_real)
    if df_adultos is not None:
        df_adultos["total_adultos"] = df_adultos["hombres_18+"] + df_adultos["mujeres_18+"]
        plot_top_locations(
            df_adultos,
            x_col="distrito_real",  # Actualizado a distrito_real
            y_col="total_adultos",
            title="Distritos con Mayor Población Adulta - 2015",
            filename="top_distritos_2015.png"
        )

def graph_2020():
    print("\n📊 Generando gráficas para INE 2020...")
    
    # 1. Comparativa hombres vs mujeres por distrito REAL
    df_adultos = load_data("poblacion_adulta_2020")
    if df_adultos is not None:
        plot_gender_comparison(
            df_adultos,
            x_col="distrito_real",  # Actualizado a distrito_real
            male_col="hombres_18+",
            female_col="mujeres_18+",
            title="Población Adulta por Distrito y Sexo - Jalisco 2020",
            filename="adultos_sexo_distrito_2020.png"
        )
    
    # 2. Resumen Jalisco
    df_jalisco = load_data("resumen_jalisco_2020")
    if df_jalisco is not None:
        plot_gender_comparison(
            df_jalisco,
            x_col="entidad",
            male_col="hombres_18+",
            female_col="mujeres_18+",
            title="Población Adulta Total - Jalisco 2020",
            filename="adultos_sexo_jalisco_2020.png"
        )

def graph_2025():
    print("\n📊 Generando gráficas para INE 2025...")
    
    # 1. Comparativa hombres vs mujeres por distrito REAL
    df_distritos = load_data("poblacion_adulta_distrito_2025")
    if df_distritos is not None:
        plot_gender_comparison(
            df_distritos,
            x_col="distrito_real",  # Actualizado a distrito_real
            male_col="hombres_18+",
            female_col="mujeres_18+",
            title="Población Adulta por Distrito - Jalisco 2025",
            filename="adultos_sexo_distrito_2025.png"
        )
    
    # 2. Top municipios ZMG
    df_municipios = load_data("poblacion_adulta_municipio_2025")
    if df_municipios is not None:
        # Filtrar municipios ZMG (códigos hipotéticos)
        zmg_codes = [14, 39, 67, 98, 120]  # Actualizar con códigos reales
        df_zmj = df_municipios[df_municipios["clave_municipio"].isin(zmg_codes)]
        
        plot_gender_comparison(
            df_zmj,
            x_col="nombre_municipio",
            male_col="hombres_18+",
            female_col="mujeres_18+",
            title="Población Adulta en ZMG - 2025",
            filename="adultos_sexo_zmj_2025.png"
        )
        
        # 3. Enfoque especial en Guadalajara
        df_gdl = df_municipios[df_municipios["nombre_municipio"].str.contains("Guadalajara")]
        if not df_gdl.empty:
            plot_gender_comparison(
                df_gdl,
                x_col="nombre_municipio",
                male_col="hombres_18+",
                female_col="mujeres_18+",
                title="Población Adulta en Guadalajara - 2025",
                filename="adultos_sexo_gdl_2025.png"
            )

def main():
    print("="*50)
    print("INICIANDO GENERACIÓN DE VISUALIZACIONES OPTIMIZADAS")
    print("="*50)
    
    graph_2015()
    graph_2020()
    graph_2025()
    
    print("\n" + "="*50)
    print(f"✅ Todas las gráficas guardadas en: {STAT_GRAPHS}")
    print("="*50)

if __name__ == "__main__":
    main()