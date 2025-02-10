# scraper/benalmadena_scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import re

class BenalmadenaScraper:
    """
    Scraper para la tabla de tarifas de Puerto Benalmádena.
    Retorna una lista de diccionarios con la info parseada,
    en lugar de insertar directamente en la base de datos.
    """

    def __init__(self, url: str):
        """
        :param url: URL de la página de Tarifas
        """
        self.url = url

    def scrape(self) -> List[Dict]:
        """
        Realiza la petición HTTP a la URL, parsea las tablas
        y retorna una lista con todos los registros extraídos.
        """
        print(f"[SCRAPER] Scraping URL: {self.url}")
        response = requests.get(self.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extraemos datos de las tablas relevantes (tablepress-17, -18, -19, etc.)
        t1_data = self.parse_table_17(soup)  # T.1: Tarifas diarias
        t2_data = self.parse_table_18(soup)  # Exceso de medidas
        t4_elec = self.parse_table_19(soup)  # Electricidad
        t4_agua = self.parse_table_20(soup)  # Agua
        t4_enchufes = self.parse_table_21(soup)  # Enchufes

        # Combinamos todo en un solo array
        all_data = t1_data + t2_data + t4_elec + t4_agua + t4_enchufes

        print(f"[SCRAPER] Total registros extraídos de Puerto Benalmadena: {len(all_data)}\n")
        return all_data

    def parse_table_17(self, soup: BeautifulSoup) -> List[Dict]:
        """
        T.1 TARIFAS DIARIAS DE ALQUILER DE AMARRES
        - ID tabla: tablepress-17
        Estructura:
            ESLORLA | MANGA | (TEMPORADA ALTA) | (TEMPORADA BAJA)
        """
        table = soup.find("table", {"id": "tablepress-17"})
        if not table:
            print("[SCRAPER] No se encontró tablepress-17.")
            return []

        rows = table.find_all("tr")[2:]  # saltamos 2 filas de cabecera
        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            try:
                eslora_str = cols[0].get_text(strip=True)
                manga_str  = cols[1].get_text(strip=True)
                alta_str   = cols[2].get_text(strip=True)
                baja_str   = cols[3].get_text(strip=True)

                eslora = float(eslora_str.replace(",", "."))
                manga  = float(manga_str.replace(",", "."))

                alta_val = self.extract_numeric(alta_str)  # p.ej 6.2513
                baja_val = self.extract_numeric(baja_str)

                record = {
                    "port_name": "Puerto Benalmadena",
                    "table_name": "T1 Tarifas Diarias",
                    "boat_length_min": eslora,
                    "boat_length_max": eslora,  # en este caso es único
                    "manga": manga,
                    "price_high_season": alta_val,
                    "price_low_season": baja_val,
                    "iva_included": False,
                    "water_included": False,
                    "electricity_included": False,
                    "timestamp": datetime.utcnow().isoformat()
                }

                data.append(record)
                print(f" [T1] Parsed: {record}")
            except Exception as e:
                print(f" [T1] Error parseando fila: {e}")

        print(f"[SCRAPER] T1 => {len(data)} filas extraídas.")
        return data

    def parse_table_18(self, soup: BeautifulSoup) -> List[Dict]:
        """
        EXCESO DE MEDIDAS BARCOS
        - ID tabla: tablepress-18
        Estructura: ESLORLA | MANGA | ALTA | BAJA
        """
        table = soup.find("table", {"id": "tablepress-18"})
        if not table:
            print("[SCRAPER] No se encontró tablepress-18.")
            return []

        rows = table.find_all("tr")[2:]
        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            try:
                eslora_str = cols[0].get_text(strip=True)
                manga_str  = cols[1].get_text(strip=True)
                alta_str   = cols[2].get_text(strip=True)
                baja_str   = cols[3].get_text(strip=True)

                eslora = float(eslora_str.replace(",", "."))
                manga  = float(manga_str.replace(",", "."))

                alta_val = self.extract_numeric(alta_str)
                baja_val = self.extract_numeric(baja_str)

                record = {
                    "port_name": "Puerto Benalmadena",
                    "table_name": "T2 Exceso de Medidas",
                    "boat_length_min": eslora,
                    "boat_length_max": eslora,
                    "manga": manga,
                    "price_high_season": alta_val,
                    "price_low_season": baja_val,
                    "iva_included": False,
                    "water_included": False,
                    "electricity_included": False,
                    "timestamp": datetime.utcnow().isoformat()
                }
                data.append(record)
                print(f" [T2] Parsed: {record}")
            except Exception as e:
                print(f" [T2] Error parseando fila: {e}")

        print(f"[SCRAPER] T2 => {len(data)} filas extraídas.")
        return data

    def parse_table_19(self, soup: BeautifulSoup) -> List[Dict]:
        """
        T.4 (4.1) ELECTRICIDAD
        - ID tabla: tablepress-19
        Estructura distinta, parseamos flexible:
          col0 col1 col2
        p.ej:
         "1. Con Contador" | "" | "0,4486 Kw/h"
        """
        table = soup.find("table", {"id": "tablepress-19"})
        if not table:
            print("[SCRAPER] No se encontró tablepress-19 (Electricidad).")
            return []

        rows = table.find_all("tr")
        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            left  = cols[0].get_text(strip=True)
            mid   = cols[1].get_text(strip=True)
            right = cols[2].get_text(strip=True)

            numeric_val = self.extract_numeric(right)
            record = {
                "port_name": "Puerto Benalmadena",
                "table_name": "T4.1 Electricidad",
                "description_left": left,
                "description_mid": mid,
                "price_extracted": numeric_val,
                "unit": "Kw/h" if "Kw/h" in right else "EUR/day",
                "iva_included": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            data.append(record)
            print(f" [T4-ELEC] Parsed: {record}")

        print(f"[SCRAPER] T4-ELEC => {len(data)} filas extraídas.")
        return data

    def parse_table_20(self, soup: BeautifulSoup) -> List[Dict]:
        """
        4.2 AGUA
        - ID tabla: tablepress-20
        Filas con col0, col1, col2
        """
        table = soup.find("table", {"id": "tablepress-20"})
        if not table:
            print("[SCRAPER] No se encontró tablepress-20 (Agua).")
            return []

        rows = table.find_all("tr")
        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            c0 = cols[0].get_text(strip=True)
            c1 = cols[1].get_text(strip=True)
            c2 = cols[2].get_text(strip=True)

            numeric_val = self.extract_numeric(c2)
            record = {
                "port_name": "Puerto Benalmadena",
                "table_name": "T4.2 Agua",
                "description_left": c0,
                "description_mid": c1,
                "price_extracted": numeric_val,
                "unit": "M3" if "M3" in c2 else "EUR/day",
                "iva_included": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            data.append(record)
            print(f" [T4-AGUA] Parsed: {record}")

        print(f"[SCRAPER] T4-AGUA => {len(data)} filas extraídas.")
        return data

    def parse_table_21(self, soup: BeautifulSoup) -> List[Dict]:
        """
        4.3 ENCHUFES
        - ID tabla: tablepress-21
        Filas: col0 col1
        p.ej:
           "De 32 A" | "123,5587 Ud."
        """
        table = soup.find("table", {"id": "tablepress-21"})
        if not table:
            print("[SCRAPER] No se encontró tablepress-21 (Enchufes).")
            return []

        rows = table.find_all("tr")
        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            c0 = cols[0].get_text(strip=True)
            c1 = cols[1].get_text(strip=True)

            numeric_val = self.extract_numeric(c1)
            record = {
                "port_name": "Puerto Benalmadena",
                "table_name": "T4.3 Enchufes",
                "description_left": c0,
                "price_extracted": numeric_val,
                "unit": "Ud." if "Ud." in c1 else "",
                "iva_included": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            data.append(record)
            print(f" [T4-ENCHUFES] Parsed: {record}")

        print(f"[SCRAPER] T4-ENCHUFES => {len(data)} filas extraídas.")
        return data

    def extract_numeric(self, text: str) -> float:
        """
        Extrae el primer número flotante de un texto,
        convirtiendo comas en punto.
        Ejemplo:
            "6,2513 €/día" => 6.2513
            "0,4486 Kw/h"  => 0.4486
        """
        if not text:
            return 0.0
        text = text.replace(",", ".")
        match = re.search(r"\d+(\.\d+)?", text)
        if match:
            return float(match.group(0))
        return 0.0
