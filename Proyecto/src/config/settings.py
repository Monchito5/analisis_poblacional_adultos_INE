# Configuración general
import sys
from pathlib import Path

# 1. Base del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

# 2. Nombres de los datasets
DATASETS = ["eige_2015", "ine_2020", "ine_2025"]

# 3. Directorios de datos y salida
RAW_DIR       = BASE_DIR / "data" / "raw"
PREPARED_DIR  = BASE_DIR / "data" / "prepared"
OUTPUT_DIR       = BASE_DIR / "out"
ABSTRACT_DIR  = OUTPUT_DIR  / "abstract_data"
IMG_DIR       = OUTPUT_DIR  / "img"
SCREENSHOTS   = IMG_DIR  / "screenshots"
STAT_GRAPHS   = IMG_DIR  / "statistical_graphs"
INTERACTIVE_DIR = BASE_DIR / "out" / "interactive"

# 4. Rutas automáticas por dataset
PATHS = {
    ds: {
        "raw":      RAW_DIR / f"{ds}.csv",
        "prepared": PREPARED_DIR / f"{ds}_prepared.csv",
        "abstract": ABSTRACT_DIR / f"resumen_{ds.split('_')[1]}.csv"
    }
    for ds in DATASETS
}

# 5. Crear directorios si no existen
for folder in (
    RAW_DIR, PREPARED_DIR,
    ABSTRACT_DIR,
    SCREENSHOTS, STAT_GRAPHS, INTERACTIVE_DIR
):
    folder.mkdir(parents=True, exist_ok=True)
