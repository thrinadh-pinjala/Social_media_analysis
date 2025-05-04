@echo off
echo Starting Flask Server...
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1
set PYTHONPATH=%PYTHONPATH%;%CD%
python -m flask run --host=0.0.0.0 --port=5000 