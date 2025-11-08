# Videre - Justfile
# Run `just --list` to see all available commands

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

# === Backend Commands ===

# Install backend dependencies
install-backend:
    cd backend && uv venv && uv pip install -e .

# Install backend dev dependencies
install-backend-dev:
    cd backend && uv venv && uv pip install -e ".[dev]"

# Run backend server
dev-backend:
    cd backend && flask --app videre.app run --debug --host 0.0.0.0 --port 5000


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
    rm -rf frontend/node_modules
    rm -rf backend/output
    rm -rf backend/tmp
    rm -rf backend/.mypy_cache
    rm -rf backend/.ruff_cache
    rm -rf backend/.venv
    rm -rf .claude/
    rm -rf .mypy_cache/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Setup project from scratch
setup: install
    @echo "Setting up backend environment..."
    @test -f backend/.env || cp backend/.env.example backend/.env
    @echo "Setup complete! Edit backend/.env with your API keys"
    @echo "Then run 'just dev' to start development servers"

# Reset the project (clean and setup)
reset: clean setup