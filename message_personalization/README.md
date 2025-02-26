# Personalizador de Mensajes AI

Esta herramienta permite generar mensajes personalizados para potenciales clientes utilizando la API de Google Gemini.

## Requisitos

- Python 3.8+
- Acceso a la API de Google Gemini (APIKey)

## Instalación

1. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

2. Configurar la API key en el archivo `.env`:

```
GOOGLE_API_KEY=your_api_key_here
```

## Ejecución

Iniciar la aplicación con:

```bash
streamlit run dashboard.py
```

## Uso de la Aplicación

### Panel Principal

1. **Configuración** (Panel izquierdo):
   - **Directrices**: Ingresa las instrucciones generales para la generación de mensajes.
   - **Plantilla de mensaje**: Crea una plantilla con campos entre corchetes, ejemplo: `Hola [nombre]`.

2. **Tabla de Empresas**:
   - En la columna izquierda, ingresa la información de cada empresa.
   - Los mensajes generados aparecerán en la columna derecha.
   - Usa el botón "+" para agregar más empresas.

3. **Acciones**:
   - **Generar**: Crea mensajes personalizados para todas las empresas.
   - **Limpiar**: Elimina todos los datos de la tabla actual.

### Historial

- Accede al historial de mensajes generados anteriormente.
- Utiliza el campo de búsqueda para filtrar mensajes.
- Cada mensaje puede expandirse para ver todos los detalles.

## Soporte

Para cualquier problema o pregunta, por favor contacta al desarrollador.
