"""
- manten un lenguaje profesional
- mostrate amigable e interesado en conocer más sobre la situación del cliente en cada mensaje 
- usa un acento argentino, no neutro
- el mensaje se enviara automaticamente así que si no tienes datos necesarios no los uses, no dejes [campos] incompletos
- no abras frases con los signos ¿ o ¡, mantente algo informal en ese aspecto
- evita usar tildes siempre, escribe algunas palabras sin la tilde correspondiente
- el mensaje debe parecer generado a mano por un humano que manda muchos mensajes personalizados, no debe estar perfecto ni parecer una inteligencia artificial.
- manten un tono calmo, sin mucha emoción

Hola, Cómo [nombre] estás? Espero que  bien. Te cuento que ofrecemos soluciones que potencian [areas y procesos claves del rubro especifico, una linea] con una aplicación totalmente personalizada por nosotros, dando [beneficios clave basado en los servicios y el rubro, una linea]. Además, trabajamos con un chatbot inteligente que responde de forma natural y humana, asegurando una atención ágil y personalizada. ¿Te interesa agendar una llamada para un asesoramiento gratuito?

dueño andres, una inmobiliaria familiar en entre ríos con una buena pagina web pero muchos clientes desordenados

constructora de piscinas, maximo es el gerente comercial. empresa antigua, con muchos clientes pero dificultad de apalancarse de esa base de datos para realizar operaciones comerciales inteligentes

"""


import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from message_generator import generate_message
import csv
import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("personalizador_mensajes.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("dashboard")

logger.info("Iniciando aplicación de Personalizador de Mensajes")

# Cargar variables de entorno
load_dotenv()
logger.debug("Variables de entorno cargadas")

# Configurar la página
st.set_page_config(
    page_title="Personalizador de Mensajes",
    page_icon="💬",
    layout="wide",
)
logger.debug("Configuración de página de Streamlit completada")

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .error-message {
        color: #ff4b4b;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    .generated-message {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Función para asegurar que exista el archivo CSV
def ensure_csv_exists():
    file_path = "message_personalization/generated_messages.csv"
    if not os.path.exists(file_path):
        logger.info(f"Creando archivo CSV de mensajes en {file_path}")
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['fecha', 'directrices', 'plantilla', 'contexto', 'mensaje_generado'])
    else:
        logger.debug(f"Archivo CSV ya existe en {file_path}")
    return file_path

# Función para guardar mensaje generado
def save_message(guidelines, template, context, generated_message):
    file_path = ensure_csv_exists()
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                            guidelines, template, context, generated_message])
        logger.info("Mensaje guardado correctamente en CSV")
    except Exception as e:
        logger.error(f"Error al guardar mensaje en CSV: {str(e)}")
        raise

# Inicializar estado de sesión
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
    logger.debug("Inicializado estado de página a 'dashboard'")

if 'company_info_list' not in st.session_state:
    st.session_state.company_info_list = [{"info": "", "message": ""}]
    logger.debug("Inicializada lista de información de empresas")

if 'error_message' not in st.session_state:
    st.session_state.error_message = ""
    logger.debug("Inicializado mensaje de error")

# Barra lateral para navegación
with st.sidebar:
    st.title("Personalizador de Mensajes")
    
    # Menú de navegación
    if st.button("Panel Principal", key="dashboard_btn"):
        st.session_state.page = 'dashboard'
        logger.info("Usuario navegó a la página principal")
    if st.button("Historial de Mensajes", key="history_btn"):
        st.session_state.page = 'history'
        logger.info("Usuario navegó a la página de historial")
    
    st.divider()
    
    # Solo mostrar estos campos en el dashboard principal
    if st.session_state.page == 'dashboard':
        st.subheader("Configuración")
        
        def update_guidelines():
            logger.debug("Directrices actualizadas por el usuario")
            # No necesitas hacer nada específico aquí ya que st.session_state se actualiza automáticamente
            pass

        def update_template():
            logger.debug("Plantilla actualizada por el usuario")
            # No necesitas hacer nada específico aquí ya que st.session_state se actualiza automáticamente
            pass

        # Campos de configuración
        st.session_state.guidelines = st.text_area(
            "Directrices para la generación de mensajes",
            value=st.session_state.get('guidelines', ''),
            height=150,
            placeholder="Ej: Mensajes amigables y profesionales, incluir nombre del contacto, mencionar servicios específicos...",
            on_change=update_guidelines,
            key="guidelines_input"
        )

        st.session_state.template = st.text_area(
            "Plantilla de mensaje con [campos]",
            value=st.session_state.get('template', ''),
            height=150,
            placeholder="Ej: Hola [nombre], me gustaría hablar sobre [servicio] para su empresa...",
            on_change=update_template,
            key="template_input"
        )

# Función para agregar una nueva fila
def add_new_row():
    st.session_state.company_info_list.append({"info": "", "message": ""})
    logger.info(f"Nueva fila agregada. Total filas: {len(st.session_state.company_info_list)}")

# Función para limpiar la tabla
def clear_table():
    st.session_state.company_info_list = [{"info": "", "message": ""}]
    st.session_state.error_message = ""
    logger.info("Tabla limpiada por el usuario")

# Función para generar todos los mensajes
def generate_all_messages():
    logger.info("Iniciando proceso de generación de mensajes")
    
    # Validar campos requeridos
    if not st.session_state.guidelines.strip():
        st.session_state.error_message = "Error: El campo de directrices no puede estar vacío"
        logger.warning("Intento de generación con directrices vacías")
        return
    
    if not st.session_state.template.strip():
        st.session_state.error_message = "Error: La plantilla de mensaje no puede estar vacía"
        logger.warning("Intento de generación con plantilla vacía")
        return
    
    # Validar que todas las filas tienen información
    empty_rows = [i+1 for i, row in enumerate(st.session_state.company_info_list) if not row["info"].strip()]
    if empty_rows:
        row_numbers = ", ".join(map(str, empty_rows))
        st.session_state.error_message = f"Error: La información de empresa está vacía en las filas: {row_numbers}"
        logger.warning(f"Intento de generación con filas vacías: {row_numbers}")
        return
    
    # Limpiar mensaje de error si todo está correcto
    st.session_state.error_message = ""
    
    # Generar mensajes para cada fila
    logger.info(f"Generando mensajes para {len(st.session_state.company_info_list)} empresas")
    for i, row in enumerate(st.session_state.company_info_list):
        company_info = row["info"]
        logger.debug(f"Generando mensaje para empresa #{i+1}")
        
        try:
            response = generate_message(
                st.session_state.guidelines,
                st.session_state.template,
                company_info
            )
            
            # Guardar el mensaje generado
            save_message(
                st.session_state.guidelines,
                st.session_state.template,
                company_info,
                response
            )
            
            # Actualizar el mensaje en la lista
            st.session_state.company_info_list[i]["message"] = response
            logger.info(f"Mensaje para empresa #{i+1} generado correctamente")
        except Exception as e:
            logger.error(f"Error al generar mensaje para empresa #{i+1}: {str(e)}")
            st.session_state.company_info_list[i]["message"] = f"Error al generar mensaje: {str(e)}"
    
    logger.info("Proceso de generación de mensajes completado")

# Mostrar página correspondiente
if st.session_state.page == 'dashboard':
    logger.debug("Renderizando página principal")
    st.markdown('<div class="main-header">Panel de Personalización de Mensajes</div>', unsafe_allow_html=True)
    
    # Botones de acción en la parte superior derecha
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        if st.session_state.error_message:
            st.markdown(f'<div class="error-message">{st.session_state.error_message}</div>', unsafe_allow_html=True)
            logger.debug(f"Mostrando mensaje de error: {st.session_state.error_message}")
    with col2:
        st.button("Limpiar", on_click=clear_table, key="clear_btn")
    with col3:
        st.button("Generar", on_click=generate_all_messages, key="generate_btn")
    
    # Tabla con filas dinámicas
    logger.debug(f"Renderizando tabla con {len(st.session_state.company_info_list)} filas")
    for i, row in enumerate(st.session_state.company_info_list):
        cols = st.columns([1, 1, 0.1])
        
        # Columna de info de empresa
        with cols[0]:
            st.text_area(
                "Info Empresa",
                value=row["info"],
                key=f"company_info_{i}",
                height=150,
                placeholder="Información sobre la empresa, página web, servicios, etc.",
                on_change=lambda idx=i, val=cols[0]: update_company_info(idx, val),
            )
        
        # Columna de mensaje generado
        with cols[1]:
            if row["message"]:
                st.subheader("Mensaje Generado")
                st.code(row["message"], language="")
                logger.debug(f"Mostrando mensaje generado para fila #{i+1}")
            else:
                st.text_area(
                    "Mensaje Generado",
                    value="",
                    key=f"message_{i}",
                    height=150,
                    disabled=True,
                    placeholder="El mensaje generado aparecerá aquí"
                )
        
        # Botón para eliminar fila (excepto la primera)
        with cols[2]:
            if i > 0 and st.button("❌", key=f"delete_{i}"):
                st.session_state.company_info_list.pop(i)
                logger.info(f"Fila #{i+1} eliminada")
                st.rerun()
    
    # Botón para agregar nueva fila
    st.button("➕ Agregar empresa", on_click=add_new_row)
    
elif st.session_state.page == 'history':
    logger.debug("Cargando página de historial")
    from history import show_history_page
    show_history_page()

# Función para actualizar la información de la empresa
def update_company_info(idx, text_area):
    st.session_state.company_info_list[idx]["info"] = st.session_state[f"company_info_{idx}"]
    logger.debug(f"Información de empresa actualizada para fila #{idx+1}")
