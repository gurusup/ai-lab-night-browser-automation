import sqlite3
import argparse
from datetime import datetime

def view_agencies(show_last=False):
    """Muestra estadísticas y últimas agencias"""
    conn = sqlite3.connect("insurance_agencies.db")
    cursor = conn.cursor()

    # Estadísticas generales
    cursor.execute('SELECT COUNT(*) FROM agencies')
    total_agencies = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT postal_code) FROM agencies')
    unique_postcodes = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM postal_codes')
    total_postcodes = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM postal_codes WHERE last_searched_at IS NOT NULL')
    searched_postcodes = cursor.fetchone()[0]

    cursor.execute('SELECT AVG(rating) FROM agencies WHERE rating IS NOT NULL')
    avg_rating = cursor.fetchone()[0]
    avg_rating_str = f"{avg_rating:.2f}" if avg_rating else "N/A"

    print("\n📊 ESTADÍSTICAS GENERALES")
    print(f"Total agencias:          {total_agencies}")
    print(f"CPs únicos con datos:    {unique_postcodes}")
    print(f"CPs buscados:            {searched_postcodes}/{total_postcodes}")
    print(f"Rating promedio:         {avg_rating_str}")

    # Últimas 10 agencias (solo si se especifica flag)
    if show_last:
        cursor.execute('''
            SELECT name, address, phone, email, rating, reviews_count, postal_code, created_at
            FROM agencies
            ORDER BY created_at DESC
            LIMIT 10
        ''')

        agencies = cursor.fetchall()

        print("\n📋 ÚLTIMAS 10 AGENCIAS EXTRAÍDAS")

        if not agencies:
            print("No hay agencias en la base de datos")
        else:
            for i, agency in enumerate(agencies, 1):
                name, address, phone, email, rating, reviews, cp, created = agency
                rating_str = f"{rating}" if rating else "N/A"
                print(f"{i:2}. {name[:40]:40} | 📞 {phone or 'N/A':15} | ⭐ {rating_str:3} ({reviews or 0:3}) | 📮 {cp} | 📍 {address[:30]:30}")

    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ver estadísticas de agencias')
    parser.add_argument('--last', action='store_true', help='Mostrar últimas 10 agencias')
    args = parser.parse_args()
    view_agencies(show_last=args.last)
