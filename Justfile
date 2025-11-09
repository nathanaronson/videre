# Videre - Justfile
# Run `just --list` to see all available commands

set dotenv-load

# Default recipe - show help
default:
    @just --list

# === Frontend Commands ===

# Install frontend dependencies
install-frontend:
    cd frontend && npm install

# Run frontend dev server
dev-frontend:
    cd frontend && npm run dev

# Build frontend for production
build-frontend:
    cd frontend && npm run build

# Lint frontend code
lint-frontend:
    cd frontend && npm run lint

# Preview frontend production build
preview-frontend:
    cd frontend && npm run preview

# === Database Commands ===

# Check MongoDB status
db-status:
    #!/usr/bin/env bash
    if pgrep -x mongod > /dev/null; then
        echo "✓ MongoDB is running"
        mongosh --eval "db.adminCommand('ping')" --quiet 2>/dev/null || echo "MongoDB process found but connection failed"
    else
        echo "✗ MongoDB is not running"
        echo "Run 'just db-start' to start MongoDB"
    fi

# Start MongoDB
db-start:
    brew services start mongodb-community

# Stop MongoDB
db-stop:
    brew services stop mongodb-community

# Restart MongoDB
db-restart:
    brew services restart mongodb-community

# Reset MongoDB database (drops all data)
db-reset:
    #!/usr/bin/env bash
    echo "⚠️  WARNING: This will delete all data in the 'videre' database!"
    read -p "Are you sure you want to continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Dropping 'videre' database..."
        mongosh videre --eval "db.dropDatabase()" --quiet
        echo "✓ Database reset complete"
    else
        echo "Database reset cancelled"
    fi

# === Backend Commands ===

# Install backend dependencies
install-backend:
    cd backend && uv venv && uv pip install -e .

# Install backend dev dependencies
install-backend-dev:
    cd backend && uv venv && uv pip install -e ".[dev]"

# Ensure MongoDB is running
ensure-mongodb:
    #!/usr/bin/env bash
    if ! pgrep -x mongod > /dev/null; then
        echo "MongoDB is not running. Starting MongoDB..."
        brew services start mongodb-community 2>/dev/null || echo "Note: Could not start MongoDB via brew services. Please start MongoDB manually."
    else
        echo "MongoDB is already running ✓"
    fi

# Run backend server
dev-backend: ensure-mongodb
    cd backend/src/videre && uv run uvicorn videre.main:app --reload


# Lint backend code
lint-backend:
    cd backend && ruff check .

# Format backend code
fmt-backend:
    cd backend && ruff check --fix .

# Type check backend
typecheck-backend:
    cd backend && mypy src/

# === Combined Commands ===

# Install all dependencies
install: install-frontend install-backend-dev

# Run both frontend and backend dev servers (in parallel)
dev:
    @echo "Starting frontend and backend servers..."
    @just dev-frontend & just dev-backend

# Lint all code
lint: lint-frontend lint-backend

# Build everything
build: build-frontend

# Clean all build artifacts and caches
clean:
    rm -rf frontend/dist
    rm -rf backend/output
    rm -rf backend/tmp
    rm -rf backend/.mypy_cache
    rm -rf backend/.ruff_cache
    rm -rf .claude/
    rm -rf .mypy_cache/
    rm -rf backend/media/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Setup project from scratch
setup: install
    @echo "Setting up backend environment..."
    @test -f backend/.env || cp backend/.env.example backend/.env
    @echo ""
    @echo "✓ Setup complete!"
    @echo ""
    @echo "Next steps:"
    @echo "1. Edit backend/.env with your API keys"
    @echo "2. Install MongoDB: brew install mongodb-community (if not installed)"
    @echo "3. Run 'just dev' to start development servers (MongoDB will auto-start)"
    @echo ""
    @echo "Useful commands:"
    @echo "  just db-status  - Check if MongoDB is running"
    @echo "  just db-start   - Start MongoDB manually"
    @echo "  just dev        - Start frontend + backend (auto-starts MongoDB)"

# Reset the project (clean and setup)
reset: clean setup