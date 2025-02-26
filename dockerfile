FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Make sure .streamlit directories exist
RUN mkdir -p /app/.streamlit
RUN mkdir -p /app/message_personalization/.streamlit

# Copy Streamlit config if it exists
COPY message_personalization/.streamlit/config.toml /app/message_personalization/.streamlit/config.toml

EXPOSE 8501

# Use --server.baseUrlPath for older versions of Streamlit that don't read from config.toml
ENTRYPOINT ["streamlit", "run", "message_personalization/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.baseUrlPath=message_generator", "--server.enableXsrfProtection=false"]