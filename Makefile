.PHONY: setup import run view logs reset

setup:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
	@echo "✓ Entorno configurado. Edita .env con tus API keys"

import:
	venv/bin/python import_postcodes.py

run:
	venv/bin/python main.py

view:
	venv/bin/python view_agencies.py
	# venv/bin/python view_agencies.py --last

logs:
	@ls -lth logs/ | head -20

reset:
	@sqlite3 insurance_agencies.db "UPDATE postal_codes SET last_searched_at = NULL, results_count = 0, total_searches = 0"
	@echo "✓ Códigos postales reseteados"
