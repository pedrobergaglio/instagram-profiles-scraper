FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Create .streamlit directory if it doesn't exist
RUN mkdir -p message_personalization/.streamlit

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "message_personalization/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]