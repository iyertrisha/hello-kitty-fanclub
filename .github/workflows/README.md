# GitHub Actions Workflows

This directory contains automated workflows for code quality checks.

## Workflows

### 1. `lint.yml` - Code Linting

Runs linting checks on:
- **ESLint** for JavaScript/TypeScript/React files
- **Flake8** for Python files

**Triggers:**
- Pull requests to `main`, `master`, or `vineet` branches
- Pushes to `main`, `master`, or `vineet` branches

**What it checks:**
- ESLint: All `.js`, `.jsx`, `.ts`, `.tsx` files in frontend projects
- Flake8: All `.py` files in backend and blockchain modules

**Failure behavior:**
- Workflow fails if any linting errors are found
- Warnings are treated as errors (max-warnings: 0)

### 2. `format-check.yml` - Code Formatting Check

Runs formatting checks (does NOT auto-format):
- **Prettier** for JavaScript/TypeScript/React files
- **Black** for Python files

**Triggers:**
- Pull requests to `main`, `master`, or `vineet` branches
- Pushes to `main`, `master`, or `vineet` branches

**What it checks:**
- Prettier: All `.js`, `.jsx`, `.ts`, `.tsx`, `.json`, `.css`, `.scss`, `.md` files
- Black: All `.py` files in backend and blockchain modules

**Failure behavior:**
- Workflow fails if files are not properly formatted
- Uses `--check` mode (read-only, no file modifications)

## Project Structure

The workflows automatically detect and check:

### JavaScript/TypeScript Projects:
- `frontend/supplier-portal/`
- `frontend/admin-dashboard/`
- `frontend/shopkeeper-mobile/`
- `backend/whatsapp-bot/`
- `backend/blockchain/`

### Python Projects:
- `backend/` (Flask API)
- `backend/blockchain/` (Python utilities)

## Configuration

### ESLint
- Uses project-specific ESLint configs if present
- Falls back to React app defaults for React projects
- Skips projects without ESLint configuration

### Flake8
- Max line length: 120 characters
- Ignores: E203, W503 (compatibility with Black)
- Excludes: `venv`, `__pycache__`, `node_modules`, etc.

### Prettier
- Installs Prettier if not in dependencies
- Respects `.prettierignore` if present
- Falls back to `.gitignore` patterns

### Black
- Line length: 120 characters
- Excludes: `venv`, `__pycache__`, `node_modules`, `migrations`, etc.
- Check mode only (no auto-formatting)

## Dependencies Caching

Both workflows use GitHub Actions caching:
- **Node.js**: Caches `node_modules` based on `package-lock.json`
- **Python**: Caches pip packages based on `requirements.txt`

## Environment Variables

No secrets or environment variables are required for these workflows.
All checks run using standard tooling without external dependencies.

## Troubleshooting

### Workflow fails on ESLint
- Check if ESLint is installed in project dependencies
- Verify ESLint configuration exists
- Review linting errors in workflow logs

### Workflow fails on Prettier
- Install Prettier: `npm install --save-dev prettier`
- Create `.prettierignore` if needed
- Run locally: `npx prettier --check .`

### Workflow fails on Flake8
- Install Flake8: `pip install flake8`
- Review linting errors in workflow logs
- Fix code style issues or adjust Flake8 config

### Workflow fails on Black
- Install Black: `pip install black`
- Run locally: `black --check .`
- Format code: `black .` (then commit)

## Running Locally

### ESLint
```bash
cd frontend/supplier-portal
npm install
npx eslint . --ext .js,.jsx
```

### Flake8
```bash
cd backend
pip install flake8
flake8 . --max-line-length=120 --extend-ignore=E203,W503
```

### Prettier
```bash
cd frontend/supplier-portal
npm install --save-dev prettier
npx prettier --check .
```

### Black
```bash
cd backend
pip install black
black --check --line-length 120 .
```

