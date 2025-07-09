.PHONY: help db-up db-down db-reset test-lambda test-lambda-to list-migrations clean

# Default target
help:
	@echo "🚀 Database Day-2 Operations Lambda"
	@echo ""
	@echo "Database Commands:"
	@echo "  make db-up      - Start PostgreSQL container"
	@echo "  make db-down    - Stop PostgreSQL container"
	@echo "  make db-reset   - Reset database (stop, remove, start)"
	@echo ""
	@echo "Lambda Commands:"
	@echo "  make test-lambda               - Test Lambda function locally (all migrations)"
	@echo "  make test-lambda-to TARGET=002 - Test Lambda to specific revision"
	@echo "  make list-migrations           - List available migrations"
	@echo "  make clean                     - Clean temporary files"
	@echo ""

# Database operations
db-up:
	@echo "🐳 Starting PostgreSQL container..."
	@if docker ps -a --format '{{.Names}}' | grep -q '^alembic-postgres$$'; then \
		echo "📦 Container exists, restarting..."; \
		docker restart alembic-postgres; \
	else \
		echo "🆕 Creating new container..."; \
		docker run -d \
			--name alembic-postgres \
			-e POSTGRES_USER=alembic_user \
			-e POSTGRES_PASSWORD=alembic_pass \
			-e POSTGRES_DB=alembic_db \
			-p 5432:5432 \
			postgres:15-alpine; \
	fi
	@echo "⏳ Waiting for database to be ready..."
	@sleep 5

db-down:
	@echo "🛑 Stopping PostgreSQL container..."
	docker stop alembic-postgres || true
	docker rm alembic-postgres || true

db-reset: db-down db-up
	@echo "🔄 Database reset complete!"

# Lambda day-2 operations
test-lambda:
	@echo "🧪 Testing Lambda function locally..."
	nix develop --command python3 test_lambda.py $(ARGS)

test-lambda-to:
	@echo "🧪 Testing Lambda function with target revision: $(TARGET)"
	nix develop --command python3 test_lambda.py --target $(TARGET)

list-migrations:
	@echo "📋 Available migrations:"
	nix develop --command python3 test_lambda.py --list-migrations

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f *.log
	rm -f result result-*
