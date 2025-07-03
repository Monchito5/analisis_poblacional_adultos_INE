````markdown
# Proyecto Demográfico 2015–2035

**Autor**  
Guillermo Daniel Zaragoza Castro

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

---

## 2. Estructura del proyecto

```text
Proyecto/
├─ data/
│  ├─ raw/              # Datos originales descargados
│  │  ├─ eige_2015.csv
│  │  ├─ ine_2020.csv
│  │  └─ ine_2025.csv
│  └─ prepared/         # Datos ya limpiados/preparados
│     ├─ eige_2015_prepared.csv
│     ├─ ine_2020_prepared.csv
│     └─ ine_2025_prepared.csv
├─ out/
│  ├─ abstract_data/    # CSVs de resumen intermedios y finales
│  │  ├─ distribucion_distrito_eige2015.csv
│  │  ├─ distribucion_edad_eige2015.csv
│  │  ├─ correlacion_eige2015.csv
│  │  ├─ resumen_2015.csv
│  │  ├─ resumen_2020.csv
│  │  ├─ resumen_2025.csv
│  │  └─ resumen_final.csv
│  └─ img/
│     ├─ screenshots/
│     └─ statistical_graphs/
├─ src/
│  ├─ config/
│  │  └─ settings.py    # Rutas y constantes globales
│  └─ scripts/
│     ├─ cleaner.py          # Limpieza y preparación de raw → prepared
│     ├─ explorer_analysis.py# Genera tablas de análisis exploratorio
│     ├─ graph_analysis.py   # Genera gráficos a partir de los CSV de explorer
│     ├─ abstract.py         # Concatena y resume por región/año → resumen_final.csv
│     └─ aggregate_analysis.py # Construye serie histórica, proyecta y grafica
└─ README.md                # (¡tú aquí!)
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
```
