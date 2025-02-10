# scraper/marbella_scraper.py
import requests
import warnings

from urllib3.exceptions import InsecureRequestWarning

from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import re


class MarbellaScraper:
    """
    Scraper para la web de Puerto Deportivo de Marbella.
    Extrae los datos de tarifas en Temporada Baja, Alta, Anual
    y tablas de Tasas T0, devolviendo un array de diccionarios.
    """

    def __init__(self, url: str):
        """
        :param url: URL de la página de Tarifas de Puerto Marbella
        """
        self.url = url
        # Ignorar warnings de SSL
        warnings.simplefilter('ignore', InsecureRequestWarning)
    def scrape(self) -> List[Dict]:
        print(f"[SCRAPER] Scraping URL (Marbella): {self.url}")
        response = requests.get(self.url, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extraeremos 5 tablas principales:
        # 1) Temporada Baja
        # 2) Temporada Alta
        # 3) Tarifa Anual
        # 4) Tasa T0 base en puerto español
        # 5) Tasa T0 base en puerto extranjero
        # Cada una parseada con un método

        baja_data  = self.parse_temporada_baja(soup)
        alta_data  = self.parse_temporada_alta(soup)
        anual_data = self.parse_tarifa_anual(soup)
        t0_esp     = self.parse_t0_esp(soup)
        t0_ext     = self.parse_t0_ext(soup)

        all_data = baja_data + alta_data + anual_data + t0_esp + t0_ext
        print(f"[SCRAPER] Total registros extraídos de Puerto Marbella: {len(all_data)}\n")
        return all_data

    # -----------------------------------------------------
    # 1) TEMPORADA BAJA
    # -----------------------------------------------------
    def parse_temporada_baja(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Temporada Baja table:
          <table> con thead = "TEMPORADA BAJA"
          Estructura col0=Eslora, col1=PRECIO S/IVA, col2=luz, col3=agua, col4=Tasa T0?, col5=Total IVA
        """
        result = []
        # Buscamos la tabla que en <thead> contenga "TEMPORADA BAJA"
        table_baja = self.find_table_by_thead_text(soup, "TEMPORADA BAJA")
        if not table_baja:
            print("[SCRAPER] No se encontró la tabla de Temporada Baja en Marbella.")
            return result

        # Filas <tr> tras thead
        rows = table_baja.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            eslora_str = cols[0].get_text(strip=True)  # p.ej "6 x 2 m."
            sin_iva_str = cols[1].get_text(strip=True)
            luz_str = cols[2].get_text(strip=True)
            agua_str = cols[3].get_text(strip=True)
            t0_str = cols[4].get_text(strip=True)
            total_iva_str = cols[5].get_text(strip=True)

            # Extraer eslora, manga
            # Asumimos "6 x 2 m." => eslora=6, manga=2
            # Ajusta parseo
            esl, man = self.parse_eslora_manga(eslora_str)

            sin_iva_val = self.extract_numeric(sin_iva_str)
            luz_val = self.extract_numeric(luz_str)
            agua_val = self.extract_numeric(agua_str)
            t0_val = self.extract_numeric(t0_str)
            total_iva_val = self.extract_numeric(total_iva_str)

            record = {
                "port_name": "Puerto Marbella",
                "table_name": "Tarifa Diaria Temporada Baja",
                "boat_length_min": esl,
                "boat_length_max": esl,  # lo consideramos igual (o podrías usar 'man' si deseas)
                "manga": man,
                "price_without_iva": sin_iva_val,
                "price_high_season": 0.0,
                "price_low_season": sin_iva_val,  # no aplica
                "electricity_cost": luz_val,
                "water_cost": agua_val,
                "t0_cost": t0_val,
                "price_total_iva": total_iva_val,
                "season": "low",
                "iva_included": False,  # la web dice "Estos precios no incluyen IVA 21%"
                "timestamp": datetime.utcnow().isoformat(),
                "electricity_included": False,
                "water_included": False
            }
            result.append(record)
            print(f" [BAJA] {record}")

        return result

    # -----------------------------------------------------
    # 2) TEMPORADA ALTA
    # -----------------------------------------------------
    def parse_temporada_alta(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Similar a parse_temporada_baja, pero la <thead> = "TEMPORADA ALTA"
        """
        result = []
        table_alta = self.find_table_by_thead_text(soup, "TEMPORADA ALTA")
        if not table_alta:
            print("[SCRAPER] No se encontró la tabla de Temporada Alta en Marbella.")
            return result

        rows = table_alta.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            eslora_str = cols[0].get_text(strip=True)
            sin_iva_str = cols[1].get_text(strip=True)
            luz_str = cols[2].get_text(strip=True)
            agua_str = cols[3].get_text(strip=True)
            t0_str = cols[4].get_text(strip=True)
            total_iva_str = cols[5].get_text(strip=True)

            esl, man = self.parse_eslora_manga(eslora_str)
            sin_iva_val = self.extract_numeric(sin_iva_str)
            luz_val = self.extract_numeric(luz_str)
            agua_val = self.extract_numeric(agua_str)
            t0_val = self.extract_numeric(t0_str)
            total_iva_val = self.extract_numeric(total_iva_str)

            record = {
                "port_name": "Puerto Marbella",
                "table_name": "Tarifa Diaria Temporada Alta",
                "boat_length_min": esl,
                "boat_length_max": esl,
                "manga": man,
                "price_without_iva": sin_iva_val,
                "price_high_season": sin_iva_val,
                "price_low_season": 0.0,
                "electricity_cost": luz_val,
                "water_cost": agua_val,
                "t0_cost": t0_val,
                "price_total_iva": total_iva_val,
                "season": "high",
                "iva_included": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            result.append(record)
            print(f" [ALTA] {record}")

        return result

    # -----------------------------------------------------
    # 3) TARIFA ANUAL
    # -----------------------------------------------------
    def parse_tarifa_anual(self, soup: BeautifulSoup) -> List[Dict]:
        """
        <thead><th colspan="5"><strong>TARIFA ANUAL</strong></th></thead>
        Columnas:
          - Eslora (6 x 2 m.)
          - ANUAL S/IVA
          - DESCUENTO
          - Agua + luz
          - TOTAL
        """
        result = []
        table_anual = self.find_table_by_thead_text(soup, "TARIFA ANUAL")
        if not table_anual:
            print("[SCRAPER] No se encontró la tabla de Tarifa Anual en Marbella.")
            return result

        rows = table_anual.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            eslora_str = cols[0].get_text(strip=True)     # "6 x 2 m."
            anual_sin_iva_str = cols[1].get_text(strip=True)
            descuento_str = cols[2].get_text(strip=True)
            agua_luz_str = cols[3].get_text(strip=True)
            total_str = cols[4].get_text(strip=True)

            esl, man = self.parse_eslora_manga(eslora_str)
            anual_sin_iva_val = self.extract_numeric(anual_sin_iva_str)
            agua_luz_val = self.extract_numeric(agua_luz_str)
            total_val = self.extract_numeric(total_str)

            record = {
                "port_name": "Puerto Marbella",
                "table_name": "Tarifa Anual",
                "boat_length_min": esl,
                "boat_length_max": esl,
                "manga": man,
                "price_annual_without_iva": anual_sin_iva_val,
                "descuento": descuento_str,
                "agua_luz": agua_luz_val,
                "price_annual_total": total_val,
                "iva_included": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            result.append(record)
            print(f" [ANUAL] {record}")

        return result

    # -----------------------------------------------------
    # 4) T0 base en puerto ESPAÑOL
    # -----------------------------------------------------
    def parse_t0_esp(self, soup: BeautifulSoup) -> List[Dict]:
        """
        La tabla con <h4>BARCOS CON BASE EN PUERTO ESPAÑOL, EXENTO DE I.V.A.
        Columnas: TIPO / ESLORA, PRECIO
        """
        result = []
        # Buscamos la tabla con thead = "TIPO / ESLORA" y <h4> contenga "PUERTO ESPAÑOL"
        table_esp = self.find_table_by_thead_text(soup, "TIPO / ESLORA", heading="PUERTO ESPAÑOL")
        if not table_esp:
            print("[SCRAPER] No se encontró la tabla T0 base en puerto español.")
            return result

        rows = table_esp.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            tipo_eslora_str = cols[0].get_text(strip=True)  # "Motor - eslora >= 9m"
            precio_str       = cols[1].get_text(strip=True)  # "9,12€ / m2 / año"

            record = {
                "port_name": "Puerto Marbella",
                "table_name": "T0 Base Puerto Español",
                "tipo_eslora": tipo_eslora_str,
                "price_extracted": self.extract_numeric(precio_str),
                "unit": "/m2/año" if "/m2" in precio_str else "",
                "iva_included": False,  # exento
                "timestamp": datetime.utcnow().isoformat()
            }
            result.append(record)
            print(f" [T0-ESP] {record}")

        return result

    # -----------------------------------------------------
    # 5) T0 base en puerto EXTRANJERO
    # -----------------------------------------------------
    def parse_t0_ext(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Similar a parse_t0_esp, pero la <h4> contenga "PUERTO EXTRANJERO".
        """
        result = []
        table_ext = self.find_table_by_thead_text(soup, "TIPO / ESLORA", heading="PUERTO EXTRANJERO")
        if not table_ext:
            print("[SCRAPER] No se encontró la tabla T0 base en puerto extranjero.")
            return result

        rows = table_ext.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            tipo_eslora_str = cols[0].get_text(strip=True)
            precio_str       = cols[1].get_text(strip=True)

            record = {
                "port_name": "Puerto Marbella",
                "table_name": "T0 Base Puerto Extranjero",
                "tipo_eslora": tipo_eslora_str,
                "price_extracted": self.extract_numeric(precio_str),
                "unit": "/m2/día" if "/m2" in precio_str else "",
                "iva_included": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            result.append(record)
            print(f" [T0-EXT] {record}")

        return result

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------
    def find_table_by_thead_text(self, soup: BeautifulSoup, text: str, heading: str=None):
        """
        Busca una <table> que tenga un <thead> con un <th> conteniendo `text`.
        Opcionalmente, validamos que un heading <h3> o <h4> contenga `heading`.
        """
        # Si heading no es None, primero busca un heading con esa string
        if heading is not None:
            possible_heading = soup.find(lambda tag: tag.name in ("h3","h4") and heading.lower() in tag.get_text(strip=True).lower())
            if not possible_heading:
                return None
            # Buscaremos la tabla siguiente a ese heading, o algo similar.
            # A veces no es estricto. Revisemos approach simple:
            # Retornamos la primera table en su proximidad.
            nearest_table = possible_heading.find_next("table")
            if not nearest_table:
                return None
            # Comprobamos si en su thead hay un th que contenga `text`.
            thead = nearest_table.find("thead")
            if thead and text.lower() in thead.get_text(strip=True).lower():
                return nearest_table
            # no coincide
            return None
        else:
            # Caso normal: busco la table con thead conteniendo `text`.
            tables = soup.find_all("table", class_="uk-table")
            for tbl in tables:
                thead = tbl.find("thead")
                if thead and text.lower() in thead.get_text(strip=True).lower():
                    return tbl
            return None

    def parse_eslora_manga(self, s: str):
        """
        Dado un string p.ej "15 x 4,5 m."
        extrae (15.0, 4.5).
        """
        # Quito "m." y espacios
        s = s.replace("m.","").replace("m", "").replace(",",".").strip()
        # Split por 'x' => ["15 ", " 4.5 "]
        parts = s.split("x")
        if len(parts) < 2:
            # fallback
            return (0.0, 0.0)
        try:
            esl = float(parts[0])
            man = float(parts[1])
            return (esl, man)
        except:
            return (0.0, 0.0)

    def extract_numeric(self, text: str) -> float:
        """
        Extrae el primer número flotante de un texto,
        convirtiendo comas en punto.
        """
        if not text:
            return 0.0
        # Normalizar
        text = text.replace(",", ".")
        # Buscar primer float
        match = re.search(r"\d+(\.\d+)?", text)
        if match:
            return float(match.group(0))
        return 0.0
