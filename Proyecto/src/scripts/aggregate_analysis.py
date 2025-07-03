# Proyecto Minería de Datos — Proyección 2015–2035

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from scipy import stats
from matplotlib import patheffects
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
REGION_PALETTE = {
    "Jalisco": "#1f77b4",
    "ZMG": "#ff7f0e",
    "GDL": "#2ca02c"
}
GENDER_PALETTE = {
    "Hombres": "#3498db",
    "Mujeres": "#e74c3c"
}

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

# --- 5. Gráficas descriptivas y series (MEJORADAS) ---
def plot_series(all_df: pd.DataFrame):
    """Gráfica de serie histórica y proyección con estilo profesional"""
    # Preparar datos
    all_df["Tipo"] = np.where(all_df["AÑO"] <= 2025, "Histórico", "Proyección")
    
    # ====================================================================
    # VERSIÓN ESTÁTICA
    # ====================================================================
    try:
        plt.figure(figsize=(14, 8))
        ax = sns.lineplot(
            data=all_df,
            x="AÑO",
            y="POB_TOT",
            hue="REGIÓN",
            style="Tipo",
            markers=True,
            dashes=False,
            markersize=8,
            palette=REGION_PALETTE,
            linewidth=2.5
        )
        
        # Configuración estética
        plt.title("Población ≥18 años: Serie Histórica y Proyección (2015-2035)", 
                 fontsize=18, pad=15, fontweight='bold')
        plt.xlabel("Año", fontsize=14, labelpad=10)
        plt.ylabel("Población Adulta", fontsize=14, labelpad=10)
        
        # Línea vertical para separar histórico y proyección
        plt.axvline(x=2025.5, color='gray', linestyle='--', alpha=0.7)
        plt.text(2025.7, all_df["POB_TOT"].max()*0.9, "Proyección", 
                fontsize=12, rotation=90, va='top')
        
        # Formatear eje Y
        ax.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: f"{int(x/1000000)}M" if x >= 1000000 else f"{int(x/1000)}K")
        )
        
        # Añadir etiquetas para puntos finales
        for region in all_df["REGIÓN"].unique():
            last_point = all_df[(all_df["REGIÓN"] == region) & (all_df["AÑO"] == 2035)]
            if not last_point.empty:
                ax.annotate(f"{last_point['POB_TOT'].values[0]/1000000:.1f}M", 
                           (last_point["AÑO"].values[0], last_point["POB_TOT"].values[0]),
                           textcoords="offset points", xytext=(10,0), 
                           ha='left', va='center', fontsize=10,
                           bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
        
        # Aplicar estilos avanzados
        apply_advanced_styling(ax, "Población ≥18 años")
        
        # Leyenda
        plt.legend(title='Región', title_fontsize=12, fontsize=11, 
                   frameon=True, shadow=True, loc='best')
        
        # Guardar estático
        static_path = STATIC_DIR / "serie_historica_proyeccion.png"
        plt.tight_layout()
        plt.savefig(static_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Gráfico estático guardado: {static_path}")
    except Exception as e:
        print(f"❌ Error en gráfico estático: {str(e)}")
    
    # ====================================================================
    # VERSIÓN INTERACTIVA
    # ====================================================================
    try:
        # Crear figura interactiva
        fig = px.line(
            all_df,
            x="AÑO",
            y="POB_TOT",
            color="REGIÓN",
            line_dash="Tipo",
            markers=True,
            title="<b>Población ≥18 años: Serie Histórica y Proyección (2015-2035)</b>",
            labels={"POB_TOT": "Población Adulta", "AÑO": "Año"},
            color_discrete_map=REGION_PALETTE,
            height=600
        )
        
        # Añadir línea vertical para proyección
        fig.add_vline(x=2025.5, line_dash="dash", line_color="gray", opacity=0.7)
        fig.add_annotation(x=2026, y=all_df["POB_TOT"].max()*0.9, 
                          text="Proyección", showarrow=False, 
                          textangle=-90, font_size=12)
        
        # Personalizar diseño
        fig.update_layout(
            hovermode="x unified",
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(248,249,250,1)',
            title_font_size=20,
            legend_title_text='Región',
            xaxis_tickangle=0,
            font=dict(family="DejaVu Sans, sans-serif"),
            margin=dict(t=80, b=80),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        
        # Formatear tooltips
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Año: %{x}<br>Población: %{y:,.0f}<extra></extra>",
            marker=dict(size=8),
            line=dict(width=2.5)
        )
        
        # Guardar interactivo
        interactive_path = INTERACTIVE_DIR / "serie_historica_proyeccion.html"
        fig.write_html(interactive_path, include_plotlyjs='cdn')
        print(f"✅ Gráfico interactivo guardado: {interactive_path}")
    except Exception as e:
        print(f"❌ Error en gráfico interactivo: {str(e)}")

def plot_gender_composition(all_df: pd.DataFrame):
    """Gráfica de composición por género con estilo profesional"""
    # Preparar datos
    gender_df = all_df.melt(
        id_vars=["REGIÓN", "AÑO"],
        value_vars=["HOMBRES_18+", "MUJERES_18+"],
        var_name="Género",
        value_name="Población"
    )
    gender_df["Género"] = gender_df["Género"].replace({
        "HOMBRES_18+": "Hombres",
        "MUJERES_18+": "Mujeres"
    })
    
    # ====================================================================
    # VERSIÓN ESTÁTICA
    # ====================================================================
    try:
        plt.figure(figsize=(14, 8))
        ax = sns.lineplot(
            data=gender_df,
            x="AÑO",
            y="Población",
            hue="REGIÓN",
            style="Género",
            markers=True,
            dashes=[(2,2), (None, None)],
            markersize=8,
            palette=REGION_PALETTE,
            linewidth=2.5
        )
        
        # Configuración estética
        plt.title("Composición de Género: Serie Histórica y Proyección (2015-2035)", 
                 fontsize=18, pad=15, fontweight='bold')
        plt.xlabel("Año", fontsize=14, labelpad=10)
        plt.ylabel("Población Adulta", fontsize=14, labelpad=10)
        
        # Línea vertical para separar histórico y proyección
        plt.axvline(x=2025.5, color='gray', linestyle='--', alpha=0.7)
        plt.text(2025.7, gender_df["Población"].max()*0.9, "Proyección", 
                fontsize=12, rotation=90, va='top')
        
        # Formatear eje Y
        ax.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: f"{int(x/1000000)}M" if x >= 1000000 else f"{int(x/1000)}K")
        )
        
        # Aplicar estilos avanzados
        apply_advanced_styling(ax, "Composición de Género")
        
        # Leyenda
        plt.legend(title='Región/Género', title_fontsize=12, fontsize=11, 
                   frameon=True, shadow=True, loc='best')
        
        # Guardar estático
        static_path = STATIC_DIR / "composicion_genero.png"
        plt.tight_layout()
        plt.savefig(static_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Gráfico estático guardado: {static_path}")
    except Exception as e:
        print(f"❌ Error en gráfico estático: {str(e)}")
    
    # ====================================================================
    # VERSIÓN INTERACTIVA
    # ====================================================================
    try:
        # Crear figura interactiva
        fig = px.line(
            gender_df,
            x="AÑO",
            y="Población",
            color="REGIÓN",
            line_dash="Género",
            markers=True,
            title="<b>Composición de Género: Serie Histórica y Proyección (2015-2035)</b>",
            labels={"Población": "Población Adulta", "AÑO": "Año"},
            color_discrete_map=REGION_PALETTE,
            height=600
        )
        
        # Añadir línea vertical para proyección
        fig.add_vline(x=2025.5, line_dash="dash", line_color="gray", opacity=0.7)
        fig.add_annotation(x=2026, y=gender_df["Población"].max()*0.9, 
                          text="Proyección", showarrow=False, 
                          textangle=-90, font_size=12)
        
        # Personalizar diseño
        fig.update_layout(
            hovermode="x unified",
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(248,249,250,1)',
            title_font_size=20,
            legend_title_text='Región/Género',
            xaxis_tickangle=0,
            font=dict(family="DejaVu Sans, sans-serif"),
            margin=dict(t=80, b=80),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        
        # Formatear tooltips
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Año: %{x}<br>Población: %{y:,.0f}<extra></extra>",
            marker=dict(size=8),
            line=dict(width=2.5)
        )
        
        # Guardar interactivo
        interactive_path = INTERACTIVE_DIR / "composicion_genero.html"
        fig.write_html(interactive_path, include_plotlyjs='cdn')
        print(f"✅ Gráfico interactivo guardado: {interactive_path}")
    except Exception as e:
        print(f"❌ Error en gráfico interactivo: {str(e)}")

def plot_growth_rates(all_df: pd.DataFrame):
    """Gráfica de tasas de crecimiento con estilo profesional"""
    # Calcular tasas de crecimiento anual
    growth_df = all_df.sort_values(["REGIÓN", "AÑO"]).copy()
    growth_df["Tasa Crecimiento"] = growth_df.groupby("REGIÓN")["POB_TOT"].pct_change() * 100
    
    # Eliminar primera fila de cada grupo (sin dato anterior)
    growth_df = growth_df.dropna(subset=["Tasa Crecimiento"])
    
    # ====================================================================
    # VERSIÓN ESTÁTICA
    # ====================================================================
    try:
        plt.figure(figsize=(14, 8))
        ax = sns.lineplot(
            data=growth_df,
            x="AÑO",
            y="Tasa Crecimiento",
            hue="REGIÓN",
            style="REGIÓN",
            markers=True,
            dashes=False,
            markersize=8,
            palette=REGION_PALETTE,
            linewidth=2.5
        )
        
        # Configuración estética
        plt.title("Tasa de Crecimiento Anual de la Población Adulta (2016-2035)", 
                 fontsize=18, pad=15, fontweight='bold')
        plt.xlabel("Año", fontsize=14, labelpad=10)
        plt.ylabel("Tasa de Crecimiento (%)", fontsize=14, labelpad=10)
        
        # Línea horizontal en cero y línea vertical para proyección
        plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        plt.axvline(x=2025.5, color='gray', linestyle='--', alpha=0.7)
        plt.text(2025.7, growth_df["Tasa Crecimiento"].max()*0.9, "Proyección", 
                fontsize=12, rotation=90, va='top')
        
        # Aplicar estilos avanzados
        apply_advanced_styling(ax, "Tasa de Crecimiento")
        
        # Leyenda
        plt.legend(title='Región', title_fontsize=12, fontsize=11, 
                   frameon=True, shadow=True, loc='best')
        
        # Guardar estático
        static_path = STATIC_DIR / "tasas_crecimiento.png"
        plt.tight_layout()
        plt.savefig(static_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Gráfico estático guardado: {static_path}")
    except Exception as e:
        print(f"❌ Error en gráfico estático: {str(e)}")
    
    # ====================================================================
    # VERSIÓN INTERACTIVA
    # ====================================================================
    try:
        # Crear figura interactiva
        fig = px.line(
            growth_df,
            x="AÑO",
            y="Tasa Crecimiento",
            color="REGIÓN",
            markers=True,
            title="<b>Tasa de Crecimiento Anual de la Población Adulta (2016-2035)</b>",
            labels={"Tasa Crecimiento": "Tasa de Crecimiento (%)", "AÑO": "Año"},
            color_discrete_map=REGION_PALETTE,
            height=600
        )
        
        # Añadir líneas de referencia
        fig.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.3)
        fig.add_vline(x=2025.5, line_dash="dash", line_color="gray", opacity=0.7)
        fig.add_annotation(x=2026, y=growth_df["Tasa Crecimiento"].max()*0.9, 
                          text="Proyección", showarrow=False, 
                          textangle=-90, font_size=12)
        
        # Personalizar diseño
        fig.update_layout(
            hovermode="x unified",
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='rgba(248,249,250,1)',
            title_font_size=20,
            legend_title_text='Región',
            xaxis_tickangle=0,
            font=dict(family="DejaVu Sans, sans-serif"),
            margin=dict(t=80, b=80),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        
        # Formatear tooltips
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Año: %{x}<br>Tasa: %{y:.2f}%<extra></extra>",
            marker=dict(size=8),
            line=dict(width=2.5)
        )
        
        # Guardar interactivo
        interactive_path = INTERACTIVE_DIR / "tasas_crecimiento.html"
        fig.write_html(interactive_path, include_plotlyjs='cdn')
        print(f"✅ Gráfico interactivo guardado: {interactive_path}")
    except Exception as e:
        print(f"❌ Error en gráfico interactivo: {str(e)}")

# --- Main pipeline ---
def main():
    print("="*70)
    print("INICIANDO PROYECCIÓN POBLACIONAL 2015-2035".center(70))
    print("="*70)
    
    # Cargar maestro
    master_path = ABSTRACT_DIR / "resumen_final.csv"
    print(f"📂 Cargando datos desde: {master_path}")
    master = load_and_clean_master(master_path)
    print(f"✅ Datos cargados: {len(master)} registros")

    # Construir histórico e interpolar
    print("🔍 Construyendo serie histórica 2015-2025...")
    hist = build_historical(master)

    # Proyectar hacia 2035
    print("📈 Proyectando población hasta 2035...")
    future = project_to_2035(hist)

    # Concatenar todo
    all_data = pd.concat([hist, future], ignore_index=True)
    print(f"📊 Datos consolidados: {len(all_data)} registros (2015-2035)")

    # Clasificación de mayoría de género
    print("\n🔍 Analizando composición de género...")
    logistic_majority_gender(all_data)

    # Gráficas mejoradas
    print("\n🎨 Generando visualizaciones...")
    plot_series(all_data)
    plot_gender_composition(all_data)
    plot_growth_rates(all_data)
    
    # Guardar datos proyectados
    output_path = ABSTRACT_DIR / "proyeccion_2035.csv"
    all_data.to_csv(output_path, index=False)
    print(f"\n💾 Datos proyectados guardados en: {output_path}")
    
    print("\n" + "="*70)
    print("PROYECCIÓN COMPLETADA EXITOSAMENTE".center(70))
    print("="*70)
    print(f"📁 Gráficos estáticos en: {STATIC_DIR}")
    print(f"📁 Gráficos interactivos en: {INTERACTIVE_DIR}")

if __name__ == "__main__":
    main()