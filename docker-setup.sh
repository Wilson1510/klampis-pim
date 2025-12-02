#!/bin/bash

# Simple script to setup and run the application with Docker

echo "🚀 Starting KLAMPIS PIM with Docker..."

# Start the containers
docker compose up -d --build

echo "⏳ Waiting for database to be ready..."
sleep 5

# Run database migrations
echo "📦 Running database migrations..."
docker compose exec app alembic upgrade head

# Create initial user
echo "👤 Creating initial user..."
docker compose exec app python scripts/create_initial_user.py

echo "✅ Setup complete!"
echo ""
echo "📍 Application is running at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
