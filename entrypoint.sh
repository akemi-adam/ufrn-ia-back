#!/bin/sh
set -e

if [ -f manage.py ]; then
  echo "Aplicando migrations (se possível)..."
  python manage.py migrate --noinput || echo "Migrates falharam (aguardando serviço de DB ou não aplicável)"
fi

if [ -f manage.py ]; then
  echo "Iniciando servidor Django na porta 8000..."
  exec python3 -m uvicorn ufrnia.asgi:application --host 0.0.0.0 --port 8000 --reload
fi

exec "$@"