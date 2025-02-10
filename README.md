# Marine MVP: Marina Tariff & Occupancy Calculator
Este repositorio contiene un MVP (Minimum Viable Product) para la gestión de precios de amarre en puertos deportivos y la consulta de ocupación (mock). Incluye:

- Backend (FastAPI + MongoDB)
- Frontend (Streamlit)
- Scrapers (BeautifulSoup) para extraer tarifas de distintas webs (actualmente Puerto Benalmádena y Puerto de Marbella).

## Contenido
1. Requisitos
2. Estructura del Proyecto
3. Configuración Inicial
4. Instrucciones de Ejecución
5. Uso de la Aplicación
6. Detalles de Scraping
7. Notas sobre Certificados SSL
8. Contribuir
9. Licencia

## Requisitos
- Docker y Docker Compose instalados.
- Opcionalmente, Python 3.9+ si deseas ejecutar entornos locales sin Docker.

## Estructura del Proyecto

marine-mvp/

├── .env                          # Variables de entorno (ej. MONGO_URI)

├── docker-compose.yml            # Orquestación Docker (Mongo, backend, frontend)

├── requirements.txt              # Dependencias Python (si ejecutas local)

├── scraper/

│   ├── benalmadena_scraper.py    # Lógica de scraping para Puerto Benalmádena

│   ├── marbella_scraper.py       # Lógica de scraping para Puerto Marbella

│   ├── base_scraper.py           # (opcional) Clase base si la hubiera

│   └── run_scrapers.py           # Punto de entrada para ejecutar todos los scrapers

├── backend/

│   ├── main.py                   # FastAPI (endpoints: /calculate_price, /check_occupancy, etc.)

│   ├── database.py               # Conexión a MongoDB

│   ├── models.py                 # Modelos Pydantic (PriceQuery, etc.)

│   └── ...

├── frontend/

│   └── app.py                    # Streamlit (UI Mooring Calculator, Reservations, etc.)

├── certs/                        # Certificados SSL si los necesitas

└── README.md                     

## Principales Componentes
- Scraper: Extrae datos de tarifas de Benalmádena y Marbella, los cuales se guardan en MongoDB.
- Backend:
  - FastAPI que expone endpoints REST:
    -  POST /calculate_price
    -  POST /check_occupancy
  - Se conecta a MongoDB para guardar y leer datos scrapeados.
- Frontend:
  - Streamlit que provee una interfaz web:
    - Cálculo de precios de amarre.
    - Comparación entre puertos.
    - Mock de disponibilidad (ocupación).
    - Reserva (simulada) con formulario e imagen.



## Instrucciones de Ejecución
1. Clona este repositorio:

```
git clone https://github.com/tu-usuario/marine-mvp.git
cd marine-mvp
```

2. Levanta los contenedores con Docker Compose:

```
docker-compose up -d
```

Esto:

- Iniciará MongoDB.
- Levantará el contenedor del Backend (FastAPI).
- Levantará el contenedor del Frontend (Streamlit).
- 
3. Comprueba que los contenedores estén en funcionamiento:

```
docker-compose ps
```
4. Accede a la interfaz de Streamlit en tu navegador (por defecto, http://localhost:8501).


## Uso de la Aplicación
1. Mooring Calculator (pestaña principal):
   - Selecciona puerto (Benalmádena o Marbella).
   - Indica eslora, fechas de llegada y salida, si deseas electricidad/agua.
   - Pulsa "Calculate" para ver el precio estimado.
2. Compare Ports:
   - Usa los mismos datos y compara con el otro puerto.
3. Check Occupancy:
   - Devuelve una tabla mock con puertos y fechas en la base de datos para ~30 días.
4. Reservations:
   - Permite simular una reserva, ingresar datos de embarcación y mostrar una imagen de la marina.

## Detalles de Scraping
   - **Benalmádena**: scraper/benalmadena_scraper.py parsea varias tablas (tablepress-17, tablepress-18, etc.) para tarifas diarias, exceso de medidas, etc.
   - **Marbella**: scraper/marbella_scraper.py parsea tablas de temporada alta, baja, anual, etc.
   - Cada vez que inicias el contenedor, se ejecutan los scrapers (ver run_all_scrapers()), se borran datos previos en db.pricing y se insertan los nuevos.

## Notas sobre Certificados SSL
   - El dominio de Marbella (puertodeportivo.marbella.es) puede presentar problemas de verificación SSL dentro del contenedor.
   - Solución rápida (pero insegura): en marbella_scraper.py, usar requests.get(..., verify=False) e ignorar advertencias.
   - Solución ideal: instalar el CA bundle o el certificado en certs/, copiarlo a /usr/local/share/ca-certificates y update-ca-certificates en el Dockerfile. Luego, se quita verify=False.

## Contribuir
   1. Fork este repositorio.
   2. Crea una rama con tu feature o fix: git checkout -b feature/mi-mejora.
   3. Realiza tus cambios y haz commits.
   4. Envía un Pull Request detallando tus aportes.

## Roadmap (Ideas)
   - Añadir más puertos deportivos con sus scrapers.
   - Mejorar la lógica de precios si las fechas abarcan cambio de temporada.
   - Integrar un pequeño scheduler (APScheduer) para scraping diario.
   - Autenticación y guardado de reservas reales.
