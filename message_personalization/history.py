import streamlit as st
import pandas as pd
import os
import logging

# Configure logging
logger = logging.getLogger("history")

def truncate_text(text, max_length=60):
    """Trunca el texto a la longitud máxima y agrega '...' si es necesario"""
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length].rstrip() + "..."

def show_history_page():
    """
    Muestra la página de historial con mensajes generados anteriormente
    """
    logger.info("Cargando página de historial")
    st.markdown('<div class="main-header">Historial de Mensajes Generados</div>', unsafe_allow_html=True)
    
    # Verificar si existe el archivo CSV
    if not os.path.exists("message_personalization/generated_messages.csv"):
        logger.warning("Archivo de historial no encontrado")
        st.info("No hay mensajes generados todavía.")
        return
    
    try:
        # Cargar historial desde CSV
        logger.debug("Intentando cargar historial desde CSV")
        df = pd.read_csv("message_personalization/generated_messages.csv")
        logger.info(f"Historial cargado con {len(df)} registros")
        
        # Si está vacío
        if df.empty:
            logger.info("El archivo CSV existe pero está vacío")
            st.info("No hay mensajes generados todavía.")
            return
        
        # Agregar campo de búsqueda
        search_term = st.text_input("🔍 Buscar en historial:", placeholder="Ingrese texto para filtrar mensajes...")
        
        if search_term:
            logger.info(f"Usuario buscando: '{search_term}'")
            # Filtrar dataframe en todas las columnas de texto
            filtered_df = df[
                df['directrices'].str.contains(search_term, case=False, na=False) | 
                df['plantilla'].str.contains(search_term, case=False, na=False) | 
                df['contexto'].str.contains(search_term, case=False, na=False) | 
                df['mensaje_generado'].str.contains(search_term, case=False, na=False)
            ]
            logger.info(f"Búsqueda completada: {len(filtered_df)} resultados encontrados")
        else:
            filtered_df = df
            logger.debug("No se aplicó filtro de búsqueda")
        
        # Mostrar cantidad de resultados
        st.write(f"Mostrando {len(filtered_df)} de {len(df)} mensajes totales")
        
        # Mostrar historial
        logger.debug(f"Renderizando {len(filtered_df)} registros en la interfaz")
        for i, row in filtered_df.iterrows():
            # Obtener una versión truncada del contexto para el título del expander
            company_info_preview = truncate_text(row['contexto'])
            
            # Usar el preview del contexto en lugar del número de mensaje y fecha
            with st.expander(company_info_preview):
                logger.debug(f"Usuario expandió mensaje con contexto: {company_info_preview}")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Información")
                    st.write(f"**Fecha:** {row['fecha']}")
                    
                    st.write("**Directrices:**")
                    st.text_area("", value=row['directrices'], height=100, key=f"dir_{i}", disabled=True)
                    
                    st.write("**Plantilla:**")
                    st.text_area("", value=row['plantilla'], height=100, key=f"temp_{i}", disabled=True)
                    
                    st.write("**Contexto de Empresa:**")
                    st.text_area("", value=row['contexto'], height=100, key=f"ctx_{i}", disabled=True)
                
                with col2:
                    st.subheader("Mensaje Generado")
                    st.code(row['mensaje_generado'], language="")
    
    except Exception as e:
        logger.error(f"Error al cargar el historial: {str(e)}", exc_info=True)
        st.error(f"Error al cargar el historial: {str(e)}")
