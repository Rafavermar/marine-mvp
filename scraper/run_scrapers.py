# scraper/run_scrapers.py
from .benalmadena_scraper import BenalmadenaScraper
from .marbella import MarbellaScraper


# from .other_scraper import OtherMarinaScraper  # si tuvieras otro

def run_all_scrapers():
    benalmadena_url = "https://puertobenalmadena.es/tarifas/"
    marbella_url = "https://puertodeportivo.marbella.es/servicios-y-tarifas/tarifa-de-alquiler-de-atraques.html"

    # Instanciamos
    b_scraper = BenalmadenaScraper(benalmadena_url)
    data_benalmadena = b_scraper.scrape()

    m_scraper = MarbellaScraper(marbella_url)
    data_marbella = m_scraper.scrape()

    # unimos:
    return data_benalmadena + data_marbella
    #return data_benalmadena
