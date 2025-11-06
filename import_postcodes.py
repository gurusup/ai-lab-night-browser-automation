import csv
import urllib.request
from database import InsuranceDB

def download_and_import_postcodes():
    """Descarga e importa códigos postales de España desde GitHub INE"""

    url = "https://raw.githubusercontent.com/inigoflores/ds-codigos-postales-ine-es/master/data/codigos_postales_municipios.csv"

    print("Descargando códigos postales desde INE...")

    db = InsuranceDB()
    imported = 0

    try:
        with urllib.request.urlopen(url) as response:
            lines = response.read().decode('utf-8').splitlines()
            reader = csv.DictReader(lines)

            for row in reader:
                # El CSV tiene: codigo_postal, codigo_municipio, municipio, provincia
                codigo = row.get('codigo_postal', '').strip()
                municipio = row.get('municipio', '').strip()
                provincia = row.get('provincia', '').strip()

                if codigo:
                    if db.insert_postal_code(codigo, municipio, provincia):
                        imported += 1
                        if imported % 1000 == 0:
                            print(f"Importados {imported} códigos postales...")

        print(f"\n✓ Total importados: {imported} códigos postales")

        stats = db.get_stats()
        print(f"Total en DB: {stats['total_postcodes']}")

    except Exception as e:
        print(f"✗ Error descargando/importando: {str(e)}")

if __name__ == "__main__":
    download_and_import_postcodes()
