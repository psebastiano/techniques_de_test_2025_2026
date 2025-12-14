# ******************************************************
# Fichier: Makefile
# Description: Commandes d'automatisation pour le projet TdT
# ******************************************************

# Variables du VENV
PYTHON := ./tdt/Scripts/python
PIP := $(PYTHON) -m pip

# Outils de Qualité et Documentation
PYTEST := $(PYTHON) -m pytest
RUFF_CHECK := $(PYTHON) -m ruff check
PDOC := $(PYTHON) -m pdoc -o html application.triangulator_app
COVERAGE := $(PYTHON) -m coverage run -m pytest
COVERAGE_REPORT := $(PYTHON) -m coverage html
# ******************************************************
# CIBLES PRINCIPALES (PHONES)
# ******************************************************

test_all:
	@echo "Running ALL tests (including performance tests)..."
	$(PYTEST)

test_unit:
	@echo "Running Unit/Integration tests ONLY (excluding performance tests)..."
	$(PYTEST) -m "not performance"

test_perf:
	@echo "Running PERFORMANCE tests ONLY..."
	$(PYTEST) -m "performance"


.PHONY: test_debug
test_debug:
	@echo "Running Pytest tests with debug output (-s flag)..."
	$(PYTEST) -s

.PHONY: quality
quality:
	@echo "Running Ruff code quality scan..."
	$(RUFF_CHECK) .

.PHONY: doc
doc:
	@echo "Running Pdoc for HTML documentation generation..."
	$(PDOC)

.PHONY: coverage
coverage:
	@echo "Runninng Coverage on code..."
	$(COVERAGE)
	$(MAKE) coverage_report

.PHONY: coverage_report
coverage_report:
	@echo "Runninng Coverage with report on code..."
	$(COVERAGE_REPORT)


.PHONY: clean
clean:
	@echo "Suppression des fichiers de cache et de la documentation..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf html htmlcov .coverage # <-- Ajoute htmlcov et .coverage