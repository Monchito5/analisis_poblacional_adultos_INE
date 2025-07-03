# Configuración del proyecto
import sys
from pathlib import Path

# 1. Base del proyecto (calculada dinámicamente)
if getattr(sys, 'frozen', False):
    # Si estamos en un ejecutable (PyInstaller)
    BASE_DIR = Path(sys.executable).parent.resolve()
else:
    # Si estamos ejecutando desde código fuente
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 2. Nombres de los datasets
DATASETS = ["eige_2015", "ine_2020", "ine_2025"]

# 3. Directorios de datos y salida (relativos a BASE_DIR)
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# 4. Subdirectorios organizados por tipo
RAW_DIR = DATA_DIR / "raw"
PREPARED_DIR = DATA_DIR / "prepared"

ABSTRACT_DIR = OUTPUT_DIR / "abstract"
VISUALIZATIONS_DIR = OUTPUT_DIR / "visualizations"
INTERACTIVE_DIR = VISUALIZATIONS_DIR / "interactive"
STATIC_DIR = VISUALIZATIONS_DIR / "static"
SCREENSHOTS_DIR = STATIC_DIR / "screenshots"

# 5. Rutas automáticas por dataset
PATHS = {
    ds: {
        "raw": RAW_DIR / f"{ds}.csv",
        "prepared": PREPARED_DIR / f"{ds}_prepared.csv"
    }
    for ds in DATASETS
}

# 6. Crear directorios necesarios
DIRECTORIES = [
    # Directorios de datos
    RAW_DIR, PREPARED_DIR,
    
    # Directorios de salida
    ABSTRACT_DIR,
    
    # Directorios de visualización
    VISUALIZATIONS_DIR,
    INTERACTIVE_DIR,
    STATIC_DIR,
    SCREENSHOTS_DIR
]

def create_directories():
    """Crea todos los directorios necesarios si no existen"""
    for directory in DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"📂 Directorio creado/verificado: {directory}")

# 7. Configuración de regiones (para uso en otros módulos)
REGION_CONFIG = {
    "2015": {
        "Jalisco": {"entidad": 14},
        "ZMG": {"distrito_cod": [7, 8, 9, 11, 12, 13, 14, 15, 16]},
        "GDL": {"distrito_cod": [8, 9, 11, 14]}
    },
    "2020": {
        "Jalisco": {"distrito_cod": None},
        "ZMG": {"distrito_cod": [7, 8, 9, 11, 12, 13, 14, 15, 16]},
        "GDL": {"distrito_cod": [8, 9, 11, 14]}
    },
    "2025": {
        "Jalisco": {"clave_entidad": 14},
        "ZMG": {"clave_distrito": [7, 8, 9, 11, 12, 13, 14, 15, 16]},
        "GDL": {"clave_distrito": [8, 9, 11, 14]}
    }
}

# 8. Ejecutar la creación de directorios al importar
create_directories()

# 9. Información del sistema (para depuración)
SYSTEM_INFO = {
    "platform": sys.platform,
    "python_version": sys.version,
    "base_dir": str(BASE_DIR),
    "directories": [str(d) for d in DIRECTORIES]
}

if __name__ == "__main__":
    # Mostrar información de configuración al ejecutar directamente
    print("="*80)
    print("CONFIGURACIÓN DEL PROYECTO".center(80))
    print("="*80)
    print(f"📁 Directorio base: {BASE_DIR}")
    print(f"🐍 Versión de Python: {sys.version.split()[0]}")
    print(f"🖥️ Plataforma: {sys.platform}")
    print("\nDirectorios configurados:")
    for i, dir_path in enumerate(DIRECTORIES, 1):
        print(f"{i}. {dir_path}")
    print("="*80)