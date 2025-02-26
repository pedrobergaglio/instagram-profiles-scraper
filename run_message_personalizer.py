import os
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("runner")

def run_message_personalizer():
    """
    Script para ejecutar el personalizador de mensajes
    """
    logger.info("Iniciando script de ejecución del Personalizador de Mensajes")
    
    # Cambiar al directorio de la aplicación
    app_dir = os.path.join(os.path.dirname(__file__), "message_personalization")
    logger.debug(f"Directorio de aplicación: {app_dir}")
    
    # Verificar que el directorio existe
    if not os.path.exists(app_dir):
        logger.error(f"No se encontró el directorio {app_dir}")
        print(f"Error: No se encontró el directorio {app_dir}")
        sys.exit(1)
    
    # Verificar que dashboard.py existe
    dashboard_path = os.path.join(app_dir, "dashboard.py")
    if not os.path.exists(dashboard_path):
        logger.error(f"No se encontró el archivo {dashboard_path}")
        print(f"Error: No se encontró el archivo {dashboard_path}")
        sys.exit(1)
    
    # Ejecutar la aplicación Streamlit
    try:
        logger.info("Iniciando aplicación Streamlit")
        print("Iniciando Personalizador de Mensajes...")
        subprocess.run(["streamlit", "run", dashboard_path])
        logger.info("Aplicación Streamlit finalizada")
    except Exception as e:
        logger.error(f"Error al ejecutar la aplicación: {str(e)}", exc_info=True)
        print(f"Error al ejecutar la aplicación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_message_personalizer()
