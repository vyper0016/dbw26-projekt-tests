# DBW26 Project Tests

This repository contains pytest-based API tests for the DBW26 project. Tests are organized by domain in separate files.
## Structure
- `test_general.py`
- `test_mitarbeiter.py`
- `test_kunde.py`
- `test_adresse.py`
- `test_produkt.py`
- `test_bestellposition.py`
- `common.py` (shared constants such as `HOST` and required field sets)

## Prerequisites
- Python 3.9+ installed and on your PATH
- The DBW26 server running and reachable at `http://localhost:8080`

## Installation (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip pytest requests
```

## Running the tests
From the repository root (with the virtual environment activated):
```powershell
pytest
```
You can run a subset, e.g., only product tests:
```powershell
pytest test_produkt.py
```

## Notes
- Tests assume seed data from `data.sql` is loaded (for ID- and SKU-specific assertions).