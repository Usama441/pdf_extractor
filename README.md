# Statement Flow

Rails web app for bank statement extraction, backed by a Python PDF parser and Solid Queue workers.

## Docker Setup

1. Review the environment values in `.env`.
2. Build and start the stack:

```bash
docker compose up --build
```

3. Open the app at `http://localhost:3000`.

The Compose stack includes:

- `web`: Rails server
- `worker`: Solid Queue worker for background extraction jobs
- `db`: PostgreSQL 16

Useful commands:

```bash
docker compose up --build
docker compose down
docker compose logs -f web
docker compose logs -f worker
docker compose exec web bundle exec rails test
docker compose exec web /opt/pdf-extractor-venv/bin/python -m unittest discover -s python_backend/tests -v
```

If you want to change ports or database credentials, update `.env` and restart the stack.

## Production Docker Setup

Create a production env file from the example and fill in real secrets:

```bash
cp .env.production.example .env.production
bundle exec rails secret
```

Set the generated value as `SECRET_KEY_BASE`, set a strong `POSTGRES_PASSWORD`, and update `APP_HOST` plus `RAILS_ALLOWED_HOSTS`.

Build and start the production stack:

```bash
docker compose -f docker-compose.production.yml --env-file .env.production up --build -d
```

Useful production commands:

```bash
docker compose -f docker-compose.production.yml --env-file .env.production logs -f web
docker compose -f docker-compose.production.yml --env-file .env.production logs -f worker
docker compose -f docker-compose.production.yml --env-file .env.production exec web bundle exec rails db:prepare
docker compose -f docker-compose.production.yml --env-file .env.production down
```

Production notes:

- Put a reverse proxy such as Nginx, Caddy, Traefik, or a load balancer in front of `web` for TLS.
- Keep `rails_production_storage` backed up because uploaded PDFs and generated XLSX files live there.
- Keep `postgres_production_data` backed up because users, jobs, and extraction metadata live there.
- Use `.env.production` only on the server; it is ignored by git.
