# Visualización de análisis exploratorio

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
from matplotlib import patheffects
from pathlib import Path
from src.config.settings import (
    BASE_DIR,
    RAW_DIR,
    PREPARED_DIR,
    ABSTRACT_DIR,
    INTERACTIVE_DIR,
    STATIC_DIR,
    SCREENSHOTS_DIR,
    PATHS,
    REGION_CONFIG
)
# Asegurar carpetas de destino
STATIC_DIR.mkdir(parents=True, exist_ok=True)
INTERACTIVE_DIR.mkdir(parents=True, exist_ok=True)
print(f"📂 Directorio de gráficos estáticos: {STATIC_DIR}")
print(f"📂 Directorio de gráficos interactivos: {INTERACTIVE_DIR}")

# Configuración global mejorada
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.titlepad'] = 10
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelweight'] = 'bold'
sns.set_theme(style="whitegrid", context="talk", font_scale=0.9)

# Configuración de Plotly
pio.templates.default = "plotly_white"

# Paletas profesionales
GENDER_PALETTE = {"Hombres": "#3498db", "Mujeres": "#e74c3c"}
DISTRICT_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
                   "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

# Efectos de texto
TITLE_EFFECT = [patheffects.withStroke(linewidth=1, foreground='black')]
LABEL_EFFECT = [patheffects.withStroke(linewidth=2, foreground='white')]

def apply_advanced_styling(ax, title):
    """Aplica estilos avanzados a los gráficos"""
    # Fondo y cuadrícula
    ax.set_facecolor('#f8f9fa')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Bordes
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Título con efecto
    ax.title.set_path_effects(TITLE_EFFECT)
    
    # Etiquetas con efecto
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_path_effects(LABEL_EFFECT)
        label.set_fontsize(12)
    
    # Leyenda
    legend = ax.get_legend()
    if legend:
        legend.get_frame().set_alpha(0.8)
        legend.get_frame().set_edgecolor('gray')
        legend.get_frame().set_boxstyle("round,pad=0.3", rounding_size=0.2)
        for text in legend.get_texts():
            text.set_path_effects(LABEL_EFFECT)
            text.set_fontsize(11)

def load_data(filename):
    """Carga datos con verificación de existencia"""
    filepath = ABSTRACT_DIR / f"{filename}.csv"
    if not filepath.exists():
        print(f"❌ Archivo no encontrado: {filepath}")
        return None
    
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Datos cargados: {filepath.name} ({len(df)} filas)")
        return df
    except Exception as e:
        print(f"❌ Error al cargar {filepath}: {str(e)}")
        return None

def plot_gender_comparison(df, x_col, male_col, female_col, title, filename):
    """Comparativa avanzada de población por sexo"""
    if df is None or df.empty:
        print(f"⛔ Datos vacíos para {filename}")
        return
    
    print(f"📊 Generando gráfico de género: {title}")
    
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
    
    # ====================================================================
    # VERSIÓN ESTÁTICA (Matplotlib/Seaborn)
    # ====================================================================
    try:
        plt.figure(figsize=(14, 8))
        ax = sns.barplot(
            data=df_melted,
            x=x_col,
            y='poblacion',
            hue='sexo',
            palette=GENDER_PALETTE,
            estimator=sum,
            errorbar=None,
            edgecolor='black',
            linewidth=1,
            saturation=0.9
        )
        
        # Configuración estética avanzada
        plt.title(title, fontsize=18, pad=15, fontweight='bold')
        plt.xlabel(x_col.replace('_', ' ').title(), fontsize=14, labelpad=10)
        plt.ylabel('Población Adulta', fontsize=14, labelpad=10)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)
        
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
                fontweight='bold',
                color='white',
                path_effects=[patheffects.withStroke(linewidth=2, foreground='black')]
            )
        
        # Aplicar estilos avanzados
        apply_advanced_styling(ax, title)
        
        # Leyenda
        plt.legend(title='Sexo', title_fontsize=12, fontsize=11, 
                   frameon=True, shadow=True, loc='best')
        
        # Guardar estático
        static_path = STATIC_DIR / filename
        plt.tight_layout()
        plt.savefig(static_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Gráfico estático guardado: {static_path}")
    except Exception as e:
        print(f"❌ Error en gráfico estático: {str(e)}")
    
    # ====================================================================
    # VERSIÓN INTERACTIVA (Plotly)
    # ====================================================================
    try:
        # Calcular totales para tooltips
        totales = df_melted.groupby(x_col)['poblacion'].sum().reset_index()
        totales.rename(columns={'poblacion': 'total'}, inplace=True)
        df_melted = pd.merge(df_melted, totales, on=x_col)
        
        fig = px.bar(
            df_melted,
            x=x_col,
            y='poblacion',
            color='sexo',
            color_discrete_map=GENDER_PALETTE,
            title=f"<b>{title}</b>",
            text=[f"{x/1000:.1f}K" if x >= 1000 else str(int(x)) for x in df_melted['poblacion']],
            labels={'poblacion': 'Población Adulta', x_col: x_col.replace('_', ' ').title()},
            height=600,
            hover_data={'total': ':.0f'},
            hover_name=x_col
        )
        
        fig.update_traces(
            textposition='outside',
            textfont_size=12,
            marker_line=dict(width=1, color='black'),
            hovertemplate=(
                f"<b>%{{x}}</b><br>" +
                "Sexo: %{fullData.name}<br>" +
                "Población: %{y:,.0f}<br>" +
                "Total distrito: %{customdata[0]:,.0f}" +
                "<extra></extra>"
            )
        )
        
        fig.update_layout(
            hovermode="x unified",
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(248,249,250,1)',
            title_font_size=20,
            legend_title_text='Sexo',
            xaxis_tickangle=-45,
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            margin=dict(t=100, b=150),
            font=dict(family="DejaVu Sans, sans-serif")
        )
        
        # Guardar interactivo
        interactive_filename = filename.replace('.png', '.html')
        interactive_path = INTERACTIVE_DIR / interactive_filename
        fig.write_html(interactive_path, include_plotlyjs='cdn')
        print(f"✅ Gráfico interactivo guardado: {interactive_path}")
    except Exception as e:
        print(f"❌ Error en gráfico interactivo: {str(e)}")

def plot_age_distribution(df, x_col, y_col, title, filename):
    """Distribución avanzada por grupos de edad"""
    if df is None or df.empty:
        print(f"⛔ Datos vacíos para {filename}")
        return
    
    print(f"📊 Generando distribución de edad: {title}")
    
    # Ordenar por grupo de edad
    if 'grupo_edad' in df.columns:
        age_order = [
            '0a9', '10a19', '20a29', '30a39', 
            '40a49', '50a59', '60ymas', 'edadne'
        ]
        df = df.sort_values(by='grupo_edad', key=lambda x: x.map({v: i for i, v in enumerate(age_order)}))
    
    # ====================================================================
    # VERSIÓN ESTÁTICA (Matplotlib/Seaborn)
    # ====================================================================
    try:
        plt.figure(figsize=(12, 7))
        ax = sns.barplot(
            data=df,
            x=x_col,
            y=y_col,
            palette="viridis",  # Paleta secuencial
            errorbar=None,
            edgecolor='black',
            linewidth=1
        )
        
        # Configuración estética
        plt.title(title, fontsize=18, pad=15, fontweight='bold')
        plt.xlabel('Grupo de Edad', fontsize=14, labelpad=10)
        plt.ylabel('Población' if 'poblacion' in y_col else 'Porcentaje', fontsize=14, labelpad=10)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)
        
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
                fontweight='bold',
                color='white',
                path_effects=[patheffects.withStroke(linewidth=2, foreground='black')]
            )
        
        # Aplicar estilos avanzados
        apply_advanced_styling(ax, title)
        
        # Guardar estático
        static_path = STATIC_DIR / filename
        plt.tight_layout()
        plt.savefig(static_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Gráfico estático guardado: {static_path}")
    except Exception as e:
        print(f"❌ Error en gráfico estático: {str(e)}")
    
    # ====================================================================
    # VERSIÓN INTERACTIVA (Plotly)
    # ====================================================================
    try:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=x_col,
            color_discrete_sequence=px.colors.sequential.Viridis,
            title=f"<b>{title}</b>",
            text=[f"{x/1000:.1f}K" if x >= 1000 else str(int(x)) for x in df[y_col]],
            labels={y_col: 'Población' if 'poblacion' in y_col else 'Porcentaje', x_col: 'Grupo de Edad'},
            height=500
        )
        
        fig.update_traces(
            textposition='outside',
            textfont_size=12,
            marker_line=dict(width=1, color='black'),
            hovertemplate=(
                "<b>%{x}</b><br>" +
                ("Población: %{y:,.0f}" if 'poblacion' in y_col else "Porcentaje: %{y:.2f}%") +
                "<extra></extra>"
            )
        )
        
        fig.update_layout(
            hovermode="x unified",
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(248,249,250,1)',
            title_font_size=20,
            showlegend=False,
            xaxis_tickangle=-45,
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            margin=dict(t=80, b=100),
            font=dict(family="DejaVu Sans, sans-serif")
        )
        
        # Guardar interactivo
        interactive_filename = filename.replace('.png', '.html')
        interactive_path = INTERACTIVE_DIR / interactive_filename
        fig.write_html(interactive_path, include_plotlyjs='cdn')
        print(f"✅ Gráfico interactivo guardado: {interactive_path}")
    except Exception as e:
        print(f"❌ Error en gráfico interactivo: {str(e)}")

def plot_top_locations(df, x_col, y_col, title, filename, n=10):
    """Top ubicaciones con diseño avanzado"""
    if df is None or df.empty:
        print(f"⛔ Datos vacíos para {filename}")
        return
    
    print(f"📊 Generando top ubicaciones: {title}")
    
    # Ordenar y seleccionar top n
    df = df.sort_values(y_col, ascending=False).head(n)
    
    # ====================================================================
    # VERSIÓN ESTÁTICA (Matplotlib/Seaborn)
    # ====================================================================
    try:
        plt.figure(figsize=(12, 7))
        ax = sns.barplot(
            data=df,
            x=x_col,
            y=y_col,
            palette=DISTRICT_PALETTE,  # Paleta categórica
            errorbar=None,
            edgecolor='black',
            linewidth=1
        )
        
        # Configuración estética
        plt.title(title, fontsize=18, pad=15, fontweight='bold')
        plt.xlabel('')
        plt.ylabel('Población Adulta', fontsize=14, labelpad=10)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)
        
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
                fontweight='bold',
                color='white',
                path_effects=[patheffects.withStroke(linewidth=2, foreground='black')]
            )
        
        # Aplicar estilos avanzados
        apply_advanced_styling(ax, title)
        
        # Guardar estático
        static_path = STATIC_DIR / filename
        plt.tight_layout()
        plt.savefig(static_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Gráfico estático guardado: {static_path}")
    except Exception as e:
        print(f"❌ Error en gráfico estático: {str(e)}")
    
    # ====================================================================
    # VERSIÓN INTERACTIVA (Plotly)
    # ====================================================================
    try:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=x_col,
            color_discrete_sequence=DISTRICT_PALETTE,
            title=f"<b>{title}</b>",
            text=[f"{x/1000:.1f}K" for x in df[y_col]],
            labels={y_col: 'Población Adulta', x_col: 'Distrito'},
            height=500
        )
        
        fig.update_traces(
            textposition='outside',
            textfont_size=12,
            marker_line=dict(width=1, color='black'),
            hovertemplate=(
                "<b>%{x}</b><br>" +
                "Población: %{y:,.0f}" +
                "<extra></extra>"
            )
        )
        
        fig.update_layout(
            hovermode="x unified",
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(248,249,250,1)',
            title_font_size=20,
            showlegend=False,
            xaxis_tickangle=-45,
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            margin=dict(t=80, b=150),
            font=dict(family="DejaVu Sans, sans-serif")
        )
        
        # Guardar interactivo
        interactive_filename = filename.replace('.png', '.html')
        interactive_path = INTERACTIVE_DIR / interactive_filename
        fig.write_html(interactive_path, include_plotlyjs='cdn')
        print(f"✅ Gráfico interactivo guardado: {interactive_path}")
    except Exception as e:
        print(f"❌ Error en gráfico interactivo: {str(e)}")

# ========================================================================
# FUNCIONES ESPECÍFICAS POR AÑO (MANTENIDAS IGUAL)
# ========================================================================

def graph_2015():
    print("\n📊 Generando gráficas para EIGE 2015...")
    
    # 1. Comparativa hombres vs mujeres por distrito
    df_adultos = load_data("poblacion_adulta_2015")
    if df_adultos is not None:
        plot_gender_comparison(
            df_adultos,
            x_col="distrito_nombre",
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
    
    # 3. Top distritos con mayor población adulta
    if df_adultos is not None:
        df_adultos["total_adultos"] = df_adultos["hombres_18+"] + df_adultos["mujeres_18+"]
        plot_top_locations(
            df_adultos,
            x_col="distrito_nombre",
            y_col="total_adultos",
            title="Distritos con Mayor Población Adulta - 2015",
            filename="top_distritos_2015.png"
        )

def graph_2020():
    print("\n📊 Generando gráficas para INE 2020...")
    
    # 1. Comparativa hombres vs mujeres por distrito
    df_adultos = load_data("poblacion_adulta_2020")
    if df_adultos is not None:
        plot_gender_comparison(
            df_adultos,
            x_col="distrito_nombre",
            male_col="hombres_18+",
            female_col="mujeres_18+",
            title="Población Adulta por Distrito y Sexo - Jalisco 2020",
            filename="adultos_sexo_distrito_2020.png"
        )

    # 2. Resumen Jalisco
    df_jalisco = load_data("resumen_jalisco_2020")
    if df_jalisco is not None:
        # Traducir etiquetas
        df_jalisco['entidad'] = df_jalisco['entidad'].replace({14: "Jalisco"})
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
    
    # 1. Comparativa hombres vs mujeres por distrito
    df_distritos = load_data("poblacion_adulta_distrito_2025")
    if df_distritos is not None:
        plot_gender_comparison(
            df_distritos,
            x_col="distrito_nombre",
            male_col="hombres_18+",
            female_col="mujeres_18+",
            title="Población Adulta por Distrito - Jalisco 2025",
            filename="adultos_sexo_distrito_2025.png"
        )
    
    # 2. Top municipios ZMG
    df_municipios = load_data("poblacion_adulta_municipio_2025")
    if df_municipios is not None:
        # Filtrar municipios ZMG
        zmg_codes = [41, 120, 98, 99, 102, 46, 53] 
        df_zmg = df_municipios[df_municipios["clave_municipio"].isin(zmg_codes)]
        
        plot_gender_comparison(
            df_zmg,
            x_col="nombre_municipio",
            male_col="hombres_18+",
            female_col="mujeres_18+",
            title="Población Adulta en ZMG - 2025",
            filename="adultos_sexo_zmg_2025.png"
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
    print("="*70)
    print("INICIANDO GENERACIÓN DE VISUALIZACIONES".center(70))
    print("="*70)
    
    graph_2015()
    graph_2020()
    graph_2025()
    
    print("\n" + "="*70)
    print(f"✅ Gráficos estáticos guardados en: {STATIC_DIR}".center(70))
    print(f"✅ Gráficos interactivos guardados en: {INTERACTIVE_DIR}".center(70))
    print("="*70)

if __name__ == "__main__":
    main()