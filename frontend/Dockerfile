# frontend/Dockerfile
FROM python:3.9-slim

# Crear y usar directorio de trabajo
WORKDIR /app

# Copiamos requirements del frontend
COPY requirements.txt .

# Instalar dependencias del frontend (Streamlit, requests, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Copia la carpeta images
COPY images/ /app/images/

# Copiamos el resto del frontend (incl. app.py)
COPY . .

# Exponemos el puerto de Streamlit
EXPOSE 8501

# Comando de arranque: streamlit
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
