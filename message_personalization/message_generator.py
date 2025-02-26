import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger("message_generator")

# Cargar variables de entorno
load_dotenv()
logger.debug("Variables de entorno cargadas en message_generator")

# Configurar Gemini API
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    logger.info("API de Gemini configurada correctamente")
else:
    logger.error("No se encontró la clave de API de Google en las variables de entorno")

def generate_message(guidelines, template, company_info):
    """
    Genera un mensaje personalizado utilizando la API de Google Gemini.
    
    Args:
        guidelines: Directrices para generar el mensaje
        template: Plantilla del mensaje con campos entre corchetes
        company_info: Información sobre la empresa
        
    Returns:
        El mensaje personalizado generado
    """
    if not api_key:
        logger.error("Intento de generación sin API key configurada")
        return "Error: No se encontró la clave de API de Google. Verifica el archivo .env"
    
    try:
        logger.info("Iniciando generación de mensaje con Gemini API")
        logger.debug(f"Longitud de directrices: {len(guidelines)} caracteres")
        logger.debug(f"Longitud de plantilla: {len(template)} caracteres")
        logger.debug(f"Longitud de info de empresa: {len(company_info)} caracteres")
        
        # Configurar el modelo
        model = genai.GenerativeModel('gemini-2.0-flash')
        logger.debug("Modelo gemini-2.0-flash seleccionado")
        
        # Crear el prompt para el modelo
        prompt = f"""
        You are an expert assistant in creating personalized messages for business communications in Spanish.
        
        ## INSTRUCTIONS:
        - Generate a personalized message for a potential client following the provided guidelines.
        - Use the template as a base, replacing fields in brackets with appropriate information.
        - Use the company information to personalize the content relevantly.
        - The message should be professional but conversational, and entirely in Spanish.
        - DO NOT include any additional comments, explanations or notes - only the final message.
        
        ## GUIDELINES:
        {guidelines}
        
        ## MESSAGE TEMPLATE:
        {template}
        
        ## COMPANY INFORMATION:
        {company_info}
        
        ## GENERATED MESSAGE:
        """
        
        # Llamar a la API
        logger.info("Enviando solicitud a la API de Gemini")
        start_time = __import__('time').time()
        response = model.generate_content(prompt)
        end_time = __import__('time').time()
        
        logger.info(f"Respuesta recibida de Gemini API en {end_time - start_time:.2f} segundos")
        
        # Devolver el mensaje generado
        result = response.text.strip()
        logger.debug(f"Mensaje generado con {len(result)} caracteres")
        return result
    
    except Exception as e:
        logger.error(f"Error al llamar a la API de Gemini: {str(e)}", exc_info=True)
        return f"Error al generar el mensaje: {str(e)}"
