import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger("message_generator")

# Load environment variables
load_dotenv()

# Set up the Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    logger.error("Error: GOOGLE_API_KEY not found in environment variables.")

def generate_message(guidelines, template, context):
    """
    Generate a personalized message using Google's Gemini API.
    
    Args:
        guidelines (str): Instructions for message generation
        template (str): Message template with placeholders
        context (str): Information about the company/recipient
        
    Returns:
        str: Generated message
    """
    logger.info("Iniciando generación de mensaje")
    
    if not GOOGLE_API_KEY:
        error_msg = "No se puede generar el mensaje: No se encontró la API key de Google."
        logger.error(error_msg)
        return error_msg
    
    try:
        # Set up the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Format the prompt
        prompt = f"""
        Basándote en las siguientes directrices y plantilla, genera un mensaje personalizado para la empresa descrita.
        
        DIRECTRICES:
        {guidelines}
        
        PLANTILLA:
        {template}
        
        INFORMACIÓN DE LA EMPRESA:
        {context}
        
        Genera un mensaje personalizado completo que reemplace todos los marcadores [campo] en la plantilla con información coherente del contexto.
        """
        
        # Generate the message
        response = model.generate_content(prompt)
        generated_message = response.text.strip()
        
        logger.info("Mensaje generado correctamente")
        return generated_message
        
    except Exception as e:
        error_msg = f"Error al generar mensaje: {str(e)}"
        logger.error(error_msg)
        return error_msg
