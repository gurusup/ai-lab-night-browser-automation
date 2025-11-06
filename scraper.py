import asyncio
from browser_use import Agent
from browser_use.logging_config import setup_logging as browser_use_setup_logging
from typing import List, Dict
import os
import re
import logging
from dotenv import load_dotenv

load_dotenv()

class GoogleMapsScraper:
    def __init__(self, model_name: str = "gpt-4o", log_file: str = None):
        self.model_name = model_name
        self.log_file = log_file

        # Configurar browser-use logging con archivo si se proporciona
        if log_file:
            browser_use_setup_logging(
                log_level='info',
                info_log_file=log_file,
                force_setup=True
            )

    async def search_insurance_agencies(self, postal_code: str) -> List[Dict]:
        """Busca agencias de seguros en Google Maps para un código postal"""

        task = f"""
        Busca en Google Maps agencias y corredurías de seguros cerca del código postal {postal_code} en España.

        PASOS A SEGUIR:
        1. Haz scroll hacia abajo en la lista de resultados varias veces para cargar TODOS los resultados disponibles
        2. Una vez que no aparezcan más resultados nuevos, usa el action 'extract' con esta query:

        "Extrae TODAS las agencias/corredurías de seguros visibles. Crea tabla markdown con estos headers EXACTOS:
        | Nombre del negocio | Dirección completa | Teléfono | Sitio web | Calificación | Número de reseñas |

        - 'Nombre del negocio': nombre completo
        - 'Dirección completa': dirección completa
        - 'Teléfono': número de teléfono completo (o 'No disponible')
        - 'Sitio web': URL del sitio web (o 'No disponible')
        - 'Calificación': solo el número como '4,5' (o 'No disponible')
        - 'Número de reseñas': solo el número (o '0')"

        3. Termina con 'done'

        IMPORTANTE: Extrae TODAS las agencias que encuentres, no solo 10. Haz scroll hasta el final de los resultados.
        """

        agent = Agent(
            task=task,
            model=self.model_name,
        )

        try:
            result = await agent.run()

            # El agente devolverá los resultados, aquí procesarlos
            agencies = self._parse_results(result, postal_code)
            return agencies

        except Exception as e:
            logging.error(f"Error buscando CP {postal_code}: {str(e)}")
            return []

    def _parse_results(self, result, postal_code: str) -> List[Dict]:
        """Parsea resultados del agente"""
        agencies = []

        try:
            # Browser-use devuelve objeto con history que contiene los resultados
            if not hasattr(result, 'history') or not result.history:
                return agencies

            # Buscar en el history el contenido extraído
            for item in result.history:
                if hasattr(item, 'result') and item.result:
                    for action_result in item.result:
                        if hasattr(action_result, 'extracted_content'):
                            content = action_result.extracted_content
                            agencies.extend(self._parse_markdown_table(content, postal_code))

            return agencies

        except Exception as e:
            logging.error(f"  Error parseando resultados: {str(e)}")
            return []

    def _parse_markdown_table(self, content: str, postal_code: str) -> List[Dict]:
        """Parsea tabla markdown extraída"""
        agencies = []

        try:
            if not content:
                return agencies

            # Buscar tabla en markdown
            lines = content.split('\n')
            in_table = False
            headers = []
            header_map = {}

            for line in lines:
                line = line.strip()

                if not line or line.startswith('<'):
                    continue

                # Detectar inicio de tabla (español o inglés)
                if '|' in line and ('Nombre del negocio' in line or 'Business Name' in line):
                    headers = [h.strip() for h in line.split('|') if h.strip()]

                    # Mapear headers a índices (soporta español e inglés)
                    for i, h in enumerate(headers):
                        h_lower = h.lower()
                        if 'nombre' in h_lower or 'name' in h_lower:
                            header_map['name'] = i
                        elif 'dirección' in h_lower or 'address' in h_lower:
                            header_map['address'] = i
                        elif 'teléfono' in h_lower or 'phone' in h_lower:
                            header_map['phone'] = i
                        elif 'sitio' in h_lower or 'website' in h_lower:
                            header_map['website'] = i
                        elif 'calificación' in h_lower or 'rating' in h_lower:
                            header_map['rating'] = i
                        elif 'reseñas' in h_lower or 'reviews' in h_lower:
                            header_map['reviews'] = i
                        elif 'url' in h_lower or 'maps' in h_lower:
                            header_map['url'] = i

                    in_table = True
                    continue

                # Saltar separador de tabla
                if in_table and line.startswith('|---'):
                    continue

                # Parsear fila de datos
                if in_table and '|' in line:
                    cells = [c.strip() for c in line.split('|') if c.strip()]

                    if len(cells) >= 3:  # Al menos nombre, dirección, teléfono
                        name_idx = header_map.get('name', 0)
                        addr_idx = header_map.get('address', 1)
                        phone_idx = header_map.get('phone', 2)
                        web_idx = header_map.get('website', 3)
                        rating_idx = header_map.get('rating', 4)
                        reviews_idx = header_map.get('reviews', 5)

                        agency = {
                            'name': cells[name_idx] if name_idx < len(cells) and cells[name_idx] != 'No disponible' else '',
                            'address': cells[addr_idx] if addr_idx < len(cells) and cells[addr_idx] != 'No disponible' else '',
                            'phone': cells[phone_idx] if phone_idx < len(cells) and cells[phone_idx] != 'No disponible' else '',
                            'email': '',  # No disponible en Google Maps
                            'website': self._clean_url(cells[web_idx]) if web_idx < len(cells) else '',
                            'rating': self._parse_rating(cells[rating_idx]) if rating_idx < len(cells) else None,
                            'reviews_count': self._parse_reviews(cells[reviews_idx]) if reviews_idx < len(cells) else 0,
                            'postal_code': postal_code,
                            'google_maps_url': ''
                        }

                        if agency['name']:
                            agencies.append(agency)

            return agencies

        except Exception as e:
            logging.error(f"  Error parseando tabla: {str(e)}")
            return []

    def _clean_url(self, url: str) -> str:
        """Limpia URL"""
        if not url or url == 'No disponible':
            return ''
        # Si es URL de Google Ads, extraer la real si es posible
        if '/aclk?' in url or url.startswith('/'):
            return ''
        return url

    def _parse_rating(self, rating_str: str) -> float:
        """Parsea calificación"""
        try:
            if not rating_str or rating_str == 'No disponible' or 'No hay' in rating_str:
                return None
            # Extraer número (ej: "5,0" -> 5.0)
            match = re.search(r'(\d+)[,.](\d+)', rating_str)
            if match:
                return float(f"{match.group(1)}.{match.group(2)}")
            return None
        except:
            return None

    def _parse_reviews(self, reviews_str: str) -> int:
        """Parsea número de reseñas"""
        try:
            if not reviews_str or reviews_str == 'No disponible':
                return 0
            # Extraer número
            match = re.search(r'(\d+)', reviews_str)
            if match:
                return int(match.group(1))
            return 0
        except:
            return 0

async def search_postcode(postal_code: str, log_file: str = None) -> List[Dict]:
    """Función auxiliar para buscar un código postal"""
    scraper = GoogleMapsScraper(log_file=log_file)
    return await scraper.search_insurance_agencies(postal_code)
