#!/bin/bash

set -e

echo "Deploying Task Manager API..."

# Build and start services
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec web poetry run alembic upgrade head

echo "Deployment completed successfully!"

# Show status
docker-compose -f docker-compose.prod.yml ps
