import streamlit as st
import pandas as pd
import os
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("history")

def truncate_text(text, max_length=60):
    """Trunca el texto a la longitud máxima y agrega '...' si es necesario"""
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length].rstrip() + "..."

def show_history_page():
    """
    Display the message history page
    """
    st.markdown('<div class="main-header">Historial de Mensajes</div>', unsafe_allow_html=True)
    
    # Get path to CSV file
    file_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(file_dir, "generated_messages.csv")
    
    if not os.path.exists(file_path):
        st.warning("No hay historial de mensajes disponible.")
        logger.warning("Archivo de historial no encontrado")
        return
    
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Check if file is empty or only has headers
        if df.empty:
            st.warning("El historial de mensajes está vacío.")
            logger.info("Archivo de historial vacío")
            return
            
        # Add search functionality
        search_term = st.text_input("Buscar en mensajes", key="search_input")
        
        if search_term:
            # Filter based on search term
            filtered_df = df[
                df['mensaje_generado'].str.contains(search_term, case=False, na=False) |
                df['contexto'].str.contains(search_term, case=False, na=False) |
                df['directrices'].str.contains(search_term, case=False, na=False) |
                df['plantilla'].str.contains(search_term, case=False, na=False)
            ]
            
            if filtered_df.empty:
                st.info(f"No se encontraron resultados para '{search_term}'.")
                return
                
            df = filtered_df
        
        # Sort by date descending
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values(by='fecha', ascending=False)
        
        # Display messages
        st.write(f"Total de mensajes: {len(df)}")
        
        for i, row in df.iterrows():
            with st.expander(f"{row['fecha']} - {row['contexto'][:50]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Información")
                    st.write("**Fecha:**", row['fecha'])
                    st.write("**Contexto:**", row['contexto'])
                    st.write("**Directrices:**", row['directrices'])
                    st.write("**Plantilla:**", row['plantilla'])
                
                with col2:
                    st.subheader("Mensaje Generado")
                    st.code(row['mensaje_generado'], language="")
                    
        logger.info(f"Se mostraron {len(df)} mensajes en el historial")
                    
    except Exception as e:
        st.error(f"Error al cargar el historial: {str(e)}")
        logger.error(f"Error al procesar el historial: {str(e)}")
