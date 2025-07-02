# Visualización de análisis exploratorio

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from src.config.settings import ABSTRACT_DIR, STAT_GRAPHS

# Asegurarnos de que la carpeta de destino existe
STAT_GRAPHS.mkdir(parents=True, exist_ok=True)

# Configuración global de estilos
sns.set_theme(style="whitegrid", context="notebook", font_scale=1.1)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
CUSTOM_PALETTE = sns.color_palette("Set2")

def load_data(filename):
    """Carga datos desde abstract_data con manejo de errores.
    Si 'correlacion' está en el nombre, lee la primera columna como índice."""
    filepath = ABSTRACT_DIR / f"{filename}.csv"
    try:
        if "correlacion" in filename:
            # Para matrices de correlación, usamos la primera columna como índice
            df = pd.read_csv(filepath, index_col=0)
        else:
            df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        print(f"⚠️ Archivo no encontrado: {filepath}")
        return None

def plot_bar_chart(df, x_col, y_col, title, filename, hue=None, rotation=0, annotate=True):
    """Genera gráficos de barras mejorados con porcentajes y conteos"""
    if df is None or df.empty:
        print(f"⛔ Datos vacíos para {filename}")
        return
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=df, 
        x=x_col, 
        y=y_col, 
        hue=hue,
        palette=CUSTOM_PALETTE,
        errorbar=None
    )
    
    # Configuración de títulos y etiquetas
    ax.set_title(title, fontsize=16, pad=15, fontweight='bold')
    ax.set_ylabel(y_col.replace('_', ' ').capitalize(), fontsize=12)
    ax.set_xlabel(x_col.replace('_', ' ').capitalize(), fontsize=12)

    if rotation:
        plt.xticks(rotation=rotation, ha='right' if rotation > 45 else 'center')
    if annotate:
        for container in ax.containers:
            labels = []
            for val in container.datavalues:
                if '%' in y_col:
                    labels.append(f"{val:.1f}%")
                elif val > 1000:
                    labels.append(f"{val/1000:.1f}K")
                else:
                    labels.append(f"{val:.0f}")
            ax.bar_label(
                container, 
                labels=labels,
                label_type='edge',
                padding=5,
                fontsize=10,
                color='#333333',
                fontweight='bold'
            )
    
    plt.tight_layout()
    plt.savefig(STAT_GRAPHS / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico guardado: {filename}")

def plot_heatmap(corr_df, title, filename):
    """Genera heatmaps de correlación mejorados con anotaciones"""
    if corr_df is None or corr_df.empty:
        print(f"⛔ Datos vacíos para {filename}")
        return
    
    plt.figure(figsize=(10, 8))
    
    # Máscara triangular superior
    mask = np.triu(np.ones_like(corr_df, dtype=bool))
    
    heatmap = sns.heatmap(
        corr_df, 
        annot=True, 
        cmap="coolwarm", 
        fmt=".2f", 
        linewidths=0.5,
        mask=mask,
        vmin=-1, 
        vmax=1,
        cbar_kws={'shrink': 0.8},
        annot_kws={'size': 10, 'fontweight': 'bold'}
    )
    
    # Resaltar correlaciones fuertes
    for text in heatmap.texts:
        t = float(text.get_text())
        if abs(t) > 0.7:
            text.set_fontsize(12)
            text.set_fontweight('bold')
            text.set_color('white' if abs(t) > 0.8 else 'black')
    
    plt.title(title, fontsize=16, pad=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig(STAT_GRAPHS / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico guardado: {filename}")

def plot_histogram(df, x_col, weight_col, title, filename, bins=20):
    """Genera histogramas profesionales con estadísticas"""
    if df is None or df.empty:
        print(f"⛔ Datos vacíos para {filename}")
        return
    
    plt.figure(figsize=(12, 6))

    sns.histplot(
        data=df,
        x=x_col,
        weights=weight_col,
        bins=bins,
        kde=True,
        element='step',
        stat='density',
        palette=CUSTOM_PALETTE,
        alpha=0.7
    )
    
    mean_val = df[x_col].mean()
    median_val = df[x_col].median()
    mode_val = df[x_col].mode()[0]
    
    plt.axvline(mean_val, linestyle='--', label=f'Media: {mean_val:.1f}')
    plt.axvline(median_val, linestyle='-', label=f'Mediana: {median_val:.1f}')
    plt.axvline(mode_val, linestyle='-.', label=f'Moda: {mode_val:.1f}')
    
    plt.boxplot(
        df[x_col], 
        vert=False, 
        positions=[0.05 * max(plt.ylim())], 
        widths=[0.05 * max(plt.ylim())],
        patch_artist=True,
        boxprops=dict(facecolor=CUSTOM_PALETTE[1], alpha=0.5)
    )
    
    plt.title(title, fontsize=16, pad=15, fontweight='bold')
    plt.xlabel(x_col.replace('_', ' ').capitalize(), fontsize=12)
    plt.ylabel('Densidad', fontsize=12)
    plt.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(STAT_GRAPHS / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico guardado: {filename}")

def graph_2015():
    """Visualizaciones para EIGE 2015"""
    print("\n📊 Generando gráficas para EIGE 2015...")
    
    # Distribución de población por distrito
    df_distrito = load_data("distribucion_distrito_eige2015")
    if df_distrito is not None:
        plot_bar_chart(
            df_distrito,
            x_col='distrito_cod',
            y_col='frecuencia_%',
            title="Distribución de población por distrito - EIGE 2015",
            filename="distribucion_distrito_2015.png",
            annotate=True
        )
    
    # Distribución por grupos de edad
    df_edad = load_data("distribucion_edad_eige2015")
    if df_edad is not None:
        plot_bar_chart(
            df_edad,
            x_col='grupo_edad',
            y_col='porcentaje_promedio',
            title="Distribución promedio por grupos de edad - EIGE 2015",
            filename="distribucion_edad_2015.png",
            rotation=45,
            annotate=True
        )
    
    # Correlaciones
    df_corr = load_data("correlacion_eige2015")
    if df_corr is not None:
        plot_heatmap(
            df_corr,
            title="Matriz de Correlación - EIGE 2015",
            filename="correlacion_2015.png"
        )

def graph_2020():
    """Visualizaciones para INE 2020"""
    print("\n📊 Generando gráficas para INE 2020...")
    
    df_edad = load_data("edad_ine_2020")
    if df_edad is not None:
        plot_bar_chart(
            df_edad,
            x_col='p_0a17',
            y_col='frecuencia_%',
            title="Distribución por Grupos de Edad - INE 2020",
            filename="edad_2020.png",
            annotate=True
        )
    
    df_sexo = load_data("sexo_ine_2020")
    if df_sexo is not None:
        plot_bar_chart(
            df_sexo,
            x_col='sexo',
            y_col='frecuencia_%',
            title="Distribución por Sexo - INE 2020",
            filename="sexo_2020.png",
            annotate=True
        )

def graph_2025():
    """Visualizaciones para INE 2025"""
    print("\n📊 Generando gráficas para INE 2025...")
    
    df_conteo = load_data("conteo_poblacional_ine_2025")
    if df_conteo is not None:
        plot_bar_chart(
            df_conteo,
            x_col='fuente',
            y_col='frecuencia_%',
            title="Conteo Poblacional - INE 2025",
            filename="conteo_2025.png",
            annotate=True
        )
    
    df_lista = load_data("lista_sexo_ine_2025")
    if df_lista is not None:
        plot_bar_chart(
            df_lista,
            x_col='sexo',
            y_col='frecuencia_%',
            title="Distribución por Sexo (Lista Nominal) - INE 2025",
            filename="lista_sexo_2025.png",
            annotate=True
        )
    
    df_padron = load_data("padron_sexo_ine_2025")
    if df_padron is not None:
        plot_bar_chart(
            df_padron,
            x_col='sexo',
            y_col='frecuencia_%',
            title="Distribución por Sexo (Padrón Electoral) - INE 2025",
            filename="padron_sexo_2025.png",
            annotate=True
        )

def main():
    """Función principal"""
    print("="*50)
    print("INICIANDO GENERACIÓN DE VISUALIZACIONES")
    print("="*50)
    
    graph_2015()
    graph_2020()
    graph_2025()
    
    print("\n" + "="*50)
    print(f"✅ Todas las gráficas guardadas en: {STAT_GRAPHS}")
    print("="*50)

if __name__ == "__main__":
    main()
