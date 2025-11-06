import sqlite3
import hashlib
from typing import Optional, List, Dict
from datetime import datetime

class InsuranceDB:
    def __init__(self, db_path: str = "insurance_agencies.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT,
                website TEXT,
                rating REAL,
                reviews_count INTEGER,
                postal_code TEXT NOT NULL,
                google_maps_url TEXT,
                hash TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_postal_code ON agencies(postal_code)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_hash ON agencies(hash)
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS postal_codes (
                codigo_postal TEXT PRIMARY KEY,
                municipio TEXT,
                provincia TEXT,
                last_searched_at TIMESTAMP,
                results_count INTEGER DEFAULT 0,
                total_searches INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_last_searched ON postal_codes(last_searched_at)
        ''')

        conn.commit()
        conn.close()

    def _generate_hash(self, phone: str, email: str) -> str:
        """Genera hash único basado en teléfono y email normalizado"""
        normalized = f"{phone.lower().strip()}_{email.lower().strip()}"
        return hashlib.md5(normalized.encode()).hexdigest()

    def insert_agency(self, data: Dict) -> bool:
        """Inserta agencia si no existe duplicado"""
        hash_value = self._generate_hash(data.get('phone', ''), data.get('email', ''))

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO agencies (name, address, phone, email, website, rating,
                                     reviews_count, postal_code, google_maps_url, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['name'],
                data.get('address', ''),
                data.get('phone', ''),
                data.get('email', ''),
                data.get('website', ''),
                data.get('rating', None),
                data.get('reviews_count', None),
                data['postal_code'],
                data.get('google_maps_url', ''),
                hash_value
            ))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def get_processed_postcodes(self) -> List[str]:
        """Obtiene códigos postales ya procesados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT DISTINCT postal_code FROM agencies')
        postcodes = [row[0] for row in cursor.fetchall()]

        conn.close()
        return postcodes

    def insert_postal_code(self, codigo: str, municipio: str = '', provincia: str = '') -> bool:
        """Inserta código postal si no existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO postal_codes (codigo_postal, municipio, provincia)
                VALUES (?, ?, ?)
            ''', (codigo, municipio, provincia))
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False

    def update_postal_code_search(self, codigo: str, results_count: int):
        """Actualiza fecha y resultados de búsqueda de un código postal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE postal_codes
            SET last_searched_at = ?,
                results_count = ?,
                total_searches = total_searches + 1
            WHERE codigo_postal = ?
        ''', (datetime.now(), results_count, codigo))

        conn.commit()
        conn.close()

    def get_next_postal_code(self, reference_cp: str = '41007') -> Optional[str]:
        """Obtiene siguiente código postal a buscar

        Prioriza por:
        1. Sin fecha (NULL) o fecha más antigua
        2. Más cercano a reference_cp por distancia numérica
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT codigo_postal
            FROM postal_codes
            ORDER BY
                CASE WHEN last_searched_at IS NULL THEN 0 ELSE 1 END,
                last_searched_at ASC,
                ABS(CAST(codigo_postal AS INTEGER) - ?) ASC
            LIMIT 1
        ''', (int(reference_cp),))

        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_stats(self) -> Dict:
        """Estadísticas de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM agencies')
        total = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM postal_codes')
        total_postcodes = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM postal_codes WHERE last_searched_at IS NOT NULL')
        searched_postcodes = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM postal_codes WHERE last_searched_at IS NULL')
        pending_postcodes = cursor.fetchone()[0]

        conn.close()
        return {
            'total_agencies': total,
            'total_postcodes': total_postcodes,
            'searched_postcodes': searched_postcodes,
            'pending_postcodes': pending_postcodes
        }
