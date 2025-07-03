# Proyecto Demográfico 2015–2035

**Autor**  
Guillermo Daniel Zaragoza Castro
![serie_historica_proyeccion](https://github.com/user-attachments/assets/1f6c57af-ee9c-4d15-bd3b-f4db553049ea)
![serie_historica_proyeccion_2](https://github.com/user-attachments/assets/22db68ea-ec3b-4a5c-9885-0c07fb39f70a)

---

## 1. Objetivo

Construir series históricas de población adulta (≥18 años) para:
- **Jalisco** (entidad)
- **Zona Metropolitana de Guadalajara (ZMG)**
- **Guadalajara** (GDL)

a partir de los censos y encuestas oficiales:
- Intercensal 2015 (INEGI)
- Censo 2020 (INEGI)
- Padrón y Lista Nominal 2025 (INE)

y proyectar linealmente dichas series hasta **2035**.

Métricas principales:
- **POB_TOT**: población total ≥18 años
- **HOMBRES_18+**, **MUJERES_18+**: desagregación por sexo
### Gráficas - Población adulta por sexo y distrito (2015, 2020 y 2025)
![adultos_sexo_distrito_2015](https://github.com/user-attachments/assets/6954053a-a423-4329-b2ea-9cae57586d09)
![adultos_sexo_distrito_2020](https://github.com/user-attachments/assets/9e815b91-c554-4bb7-9288-4ecb3ca114e9)
![adultos_sexo_distrito_2025](https://github.com/user-attachments/assets/beea3314-01a8-478d-b898-031428d9befe)

---

## 2. Estructura del proyecto

```text
Proyecto/
├── src/
│   ├── config/
│   │   └── settings.py        # Configuración global del proyecto
│   ├── scripts/
│   │   ├── cleaner.py         # Limpieza de datos
│   │   ├── explorer_analysis.py # Análisis exploratorio
│   │   ├── graph_analysis.py  # Generación de gráficos
│   │   ├── aggregate_analysis.py # Proyecciones poblacionales
│   │   └── abstract.py        # Generación de resúmenes
│   └── output/
│       ├── abstract/          # Datos resumidos (CSV)
│       ├── visualizations/
│       │   ├── interactive/   # Gráficos interactivos (HTML)
│       │   └── static/        # Gráficos estáticos (PNG)
├── notebooks/
│   ├── aggregate_analysis.ipynb # Dashboard interactivo
│   └── settings.ipynb # Notebook de configuración
├── data/
│   ├── raw/                   # Datos originales
│   └── prepared/              # Datos procesados
└── README.md           # (<--- tú estás aquí )
````

---

## 3. Flujo de trabajo

1. **Limpieza y preparación**

   ```bash
   python -m src.scripts.cleaner --dataset eige_2015
   python -m src.scripts.cleaner --dataset ine_2020
   python -m src.scripts.cleaner --dataset ine_2025
   ```

   → genera los archivos `*_prepared.csv` en `data/prepared/`

2. **Análisis exploratorio**

   ```bash
   python -m src.scripts.explorer_analysis
   ```

   → crea tablas CSV en `out/abstract_data/`:

   * Estadísticos descriptivos (`resumen_2015.csv`, etc.)
   * Distribuciones por distrito, grupo de edad, correlaciones…

3. **Gráficos**

   ```bash
   python -m src.scripts.graph_analysis
   ```

   → genera PNGs en `out/img/statistical_graphs/`

4. **Resumen final por región y año**

   ```bash
   python -m src.scripts.abstract
   ```

   → produce `resumen_final.csv` en `out/abstract_data/`

5. **Serie histórica y proyección**

   ```bash
   python -m src.scripts.aggregate_analysis
   ```

   →

   * Construye serie completa 2015–2025 (interpolación)
   * Proyecta hasta 2035 (regresión lineal)
   * Clasifica mayoría de género
   * Exporta gráfica de serie histórica y proyección en `out/serie_historica_proyeccion.png`

---

## 4. Detalle de módulos clave

### `cleaner.py`

* Lee raw CSV con pandas
* Filtra sólo variables necesarias
* Normaliza nombres a minúsculas
* Renombra columnas según diccionario mnemonizado
* Filtra Jalisco (cve\_ent = 14)
* Guarda CSV preparado

### `explorer_analysis.py`

* Valida columnas esenciales
* Calcula y guarda:

  * Descriptivos (`.describe()`)
  * Distribución por distrito y grupo de edad
  * Matriz de correlaciones
* Genera metadatos (filas, columnas, nombres)

### `graph_analysis.py`

* Funciones genéricas:

  * `plot_bar_chart()`
  * `plot_heatmap()`
  * `plot_histogram()`
* Carga los CSV de `abstract_data`
* Produce gráficos listos para informes

### `abstract.py`

* Define configuraciones de filtro por región:

  * **Jalisco** (entidad 14)
  * **ZMG** (distritos 7,8,9,11,12,13,14,15,16)
  * **GDL** (distritos 8,9,11,14)
* Genera un `resumen_final.csv` con:

  * Año (2015, 2020, 2025)
  * Población total y % por sexo, para cada región

### `aggregate_analysis.py`

* Lee `resumen_final.csv`, limpia outliers
* Interpola linealmente de 2015 a 2025 por región
* Proyecta hasta 2035 con regresión lineal
* Reporta métricas de ajuste (R², MSE)
* Clasifica mayoría de género (logistic regression)
* Grafica la serie histórica + proyección

---

## 5. Dependencias

* Python ≥ 3.11.5
* pandas, numpy, scipy
* scikit-learn
* matplotlib, seaborn

Instalación rápida (con venv o conda):

```bash
pip install pandas numpy scipy scikit-learn matplotlib seaborn
```

---

## 6. Contacto

Guillermo Daniel Zaragoza Castro
🔗 \[[Correo Electrónico](guillermo.zaragoza8731@alumnos.udg.mx)] – \[[Github](https://github.com/Monchito5)]

```
