import asyncio
from database import InsuranceDB
from scraper import search_postcode
import sys
import logging
from datetime import datetime
import os

async def process_continuous(max_iterations: int = None, log_file: str = None):
    """Procesa códigos postales continuamente desde DB"""
    db = InsuranceDB()

    stats = db.get_stats()
    logging.info("=== Estado Inicial ===")
    logging.info(f"Total CPs en DB: {stats['total_postcodes']}")
    logging.info(f"Pendientes: {stats['pending_postcodes']}")
    logging.info(f"Buscados: {stats['searched_postcodes']}")
    logging.info(f"Total agencias: {stats['total_agencies']}\n")

    if stats['total_postcodes'] == 0:
        logging.error("✗ No hay códigos postales en la DB")
        logging.info("Ejecuta primero: python import_postcodes.py")
        return

    iteration = 0
    while True:
        if max_iterations and iteration >= max_iterations:
            logging.info(f"\n✓ Alcanzado límite de {max_iterations} iteraciones")
            break

        postal_code = db.get_next_postal_code()

        if not postal_code:
            logging.info("\n✓ No hay más códigos postales")
            break

        iteration += 1
        logging.info(f"\n[Iteración {iteration}] Buscando CP: {postal_code}")

        try:
            agencies = await search_postcode(postal_code, log_file=log_file)

            inserted = 0
            duplicates = 0

            for agency in agencies:
                if db.insert_agency(agency):
                    inserted += 1
                    logging.info(f"  ✓ Insertada: {agency['name']}")
                else:
                    duplicates += 1
                    logging.info(f"  ⊘ Duplicada: {agency['name']}")

            total_results = len(agencies)
            db.update_postal_code_search(postal_code, total_results)

            logging.info(f"  Resultados: {total_results} encontradas ({inserted} nuevas, {duplicates} duplicadas)")

        except Exception as e:
            logging.error(f"  ✗ Error: {str(e)}")
            db.update_postal_code_search(postal_code, 0)

        # Pausa entre búsquedas
        await asyncio.sleep(2)

    stats = db.get_stats()
    logging.info(f"\n=== Estadísticas Finales ===")
    logging.info(f"Total agencias: {stats['total_agencies']}")
    logging.info(f"CPs buscados: {stats['searched_postcodes']}/{stats['total_postcodes']}")
    logging.info(f"Pendientes: {stats['pending_postcodes']}")

def setup_logging():
    """Configura logging básico - browser-use configurará el resto"""
    # Crear directorio logs si no existe
    os.makedirs('logs', exist_ok=True)

    # Timestamp para el archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/scraper_{timestamp}.log'

    # Configurar solo para nuestros logs iniciales
    # browser-use se encargará del resto cuando se inicialice
    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - [%(name)s] %(message)s')

    # Handler para consola temporal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Configurar root logger temporalmente
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    logging.info(f"Log iniciado: {log_file}")
    return log_file

async def main():
    log_file = setup_logging()

    if len(sys.argv) > 1:
        try:
            max_iterations = int(sys.argv[1])
            logging.info(f"Modo: {max_iterations} iteraciones")
        except ValueError:
            logging.error("✗ Uso: python main.py [num_iteraciones]")
            return
    else:
        max_iterations = None
        logging.info("Modo: continuo (presiona Ctrl+C para detener)")

    try:
        await process_continuous(max_iterations, log_file=log_file)
    except KeyboardInterrupt:
        logging.info("\n✓ Detenido por usuario")

    logging.info(f"Log guardado en: {log_file}")

if __name__ == "__main__":
    asyncio.run(main())
