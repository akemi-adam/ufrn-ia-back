
# Docker

O repositório contém:

- Dockerfile: imagem baseada em Python 3.11-slim com pip fixado em 25.2.
- docker-compose.yml: sobe dois serviços:
  - web: Django.
  - qdrant: qdrant/qdrant:latest (porta REST 6333).
- entrypoint.sh: aplica migrations e inicia o servidor de desenvolvimento.
- requirements.txt.

Como usar (desenvolvimento):

1. Ajuste DJANGO_SETTINGS_MODULE no docker-compose.yml para apontar para o settings do seu projeto.
2. Preencha requirements.txt com as dependências do seu projeto.
3. Rode:
   ```
   docker compose up --build
   ```
4. Acesse o Django em http://localhost:8000 e o Qdrant em http://localhost:6333

Observações:
- Em produção use um servidor WSGI (gunicorn) e configure banco de dados (Postgres, etc.) no docker-compose.
- Se precisar que o serviço web espere até o banco ou outro serviço estar pronto, considere adicionar um wait-for-it ou healthcheck.
- O entrypoint tenta aplicar migrations automaticamente; ajuste conforme fluxo do seu projeto.
