# Videre Frontend

React frontend for AI-powered video generation.

## Setup

From project root:

```bash
just install-frontend
just dev-frontend
```

Server runs on `http://localhost:5173`

## Commands

- `just dev-frontend` - Run dev server
- `just build-frontend` - Build for production
- `just lint-frontend` - Lint code
- `just preview-frontend` - Preview production build

## Dependencies

**Core:**

- React 18 + TypeScript
- Vite - Build tool
- React Router - Routing

**UI:**

- shadcn/ui - Component library
- Tailwind CSS - Styling
- Radix UI - Primitives
- Lucide - Icons

**State:**

- TanStack Query - Data fetching
- React Hook Form - Forms
- Zod - Validation
