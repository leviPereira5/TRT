# Test Execution — Lab 12

## Stack
- Language: Python 3.13
- Test framework: PyTest 9.0.3 + pytest-django 4.12.0
- Django version: 6.0.4

## Setup
1. Install dependencies:
   ```
   pip install pytest pytest-django
   ```
2. No extra environment variables required — Django uses SQLite in test mode automatically.
3. Ensure `pytest.ini` exists at the project root (already committed).

## Run all unit tests
- Command:
  ```
  python -m pytest tests/unit/ -v
  ```

## Run a single test file
- Command:
  ```
  python -m pytest tests/unit/test_validations.py -v
  python -m pytest tests/unit/test_services.py -v
  ```

## Run a single test
- Command:
  ```
  python -m pytest tests/unit/test_validations.py::TestSymbolNormalisation::test_UT01_happy_br_stock_appends_sa -v
  ```

## Notes
- Known limitations: tests that touch the database (REQ-1, REQ-8) use Django's test runner, which creates a temporary SQLite database and rolls back after each test — no production data is affected.
- Troubleshooting: if `ModuleNotFoundError: No module named 'monitor'` appears, confirm that `pytest.ini` has `pythonpath = trt_project` and that the command is run from the project root (`C:\…\TRT`).
