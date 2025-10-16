#!/bin/sh
set -e

if [ -f manage.py ]; then
  echo "Aplicando migrations (se possível)..."
  python manage.py migrate --noinput || echo "Migrates falharam (aguardando serviço de DB ou não aplicável)"
fi

if [ -f manage.py ]; then
  echo "Iniciando servidor Django na porta 8000..."
  exec python manage.py runserver 0.0.0.0:8000
fi

exec "$@"