FROM python:3.9-slim

WORKDIR /app

# Copiamos requirements del proyecto, que está en la raíz
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiamos la carpeta backend entera
COPY backend/ /app/backend

# Si necesitas scraper u otros directorios, cópialos también:
COPY scraper/ /app/scraper

# Exponemos el puerto donde correrá FastAPI
EXPOSE 8000

# Arranque
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]



