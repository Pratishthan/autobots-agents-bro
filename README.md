# autobots-agents-bro

**Business Requirements Oracle (BRO)** - An AI-powered Chainlit application for interactive business requirements elicitation and documentation.

## Overview

autobots-agents-bro is a production Chainlit application that helps users interactively define, refine, and document business requirements. Built on the Dynagent framework from autobots-devtools-shared-lib, it uses LangChain and Google Gemini to provide an intelligent conversational interface for requirements gathering.

**Key Features:**
- Interactive Chainlit web UI for requirements conversations
- Multi-agent workflow using Dynagent framework
- Document store for requirements persistence
- Batch processing capabilities
- Langfuse observability integration
- OAuth authentication support
- Docker deployment with full Langfuse stack

## Workspace Integration

This project is part of the **pk-multi workspace** and follows workspace best practices:

- **Build System:** Poetry (not hatchling or UV)
- **Virtual Environment:** Uses shared workspace `.venv` at `../venv`
- **Dependencies:** Local path dependency on `autobots-devtools-shared-lib` with `develop = true`
- **Code Quality:** Line length 100, Ruff formatter/linter, Pyright type checker
- **Testing:** Pytest with branch coverage enabled

## Project Structure

```
autobots-agents-bro/
├── src/autobots_agents_bro/        # Main package code
│   ├── __init__.py                  # Package initialization
│   ├── usecase_ui.py                # Chainlit UI entry point
│   ├── services/                    # Core services
│   │   ├── bro_batch.py             # Batch processing
│   │   ├── document_store.py        # Requirements persistence
│   │   └── markdown_exporter.py     # Export to Markdown
│   ├── utils/                       # Utility functions
│   └── py.typed                     # PEP 561 type marker
├── tests/                           # Test files
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── e2e/                         # End-to-end tests
├── sbin/                            # Scripts
│   └── run_bro.sh                   # Chainlit launch script
├── docker-compose.yml               # Full stack deployment
├── Dockerfile                       # Poetry multi-stage build
├── Makefile                         # Project commands
├── pyproject.toml                   # Poetry config & tool settings
└── poetry.toml                      # Use workspace venv
```

## Available Commands

Run from `autobots-agents-bro/` directory:

### Development Commands

```bash
# Dependencies
make install           # Install runtime dependencies only
make install-dev       # Install with dev dependencies
make install-hooks     # Install pre-commit hooks

# Testing
make test              # Run tests with coverage (default)
make test-cov          # Run tests with HTML coverage report
make test-fast         # Run tests without coverage (faster)
make test-one TEST=tests/test_file.py::test_func  # Run specific test

# Code Quality
make format            # Format code with Ruff
make lint              # Lint with Ruff (auto-fix enabled)
make check-format      # Check formatting without modifying
make type-check        # Run Pyright type checker
make all-checks        # Run all checks (format, type-check, test)

# Chainlit
make chainlit-dev      # Run Chainlit UI on port 1337

# Other
make clean             # Remove cache files and build artifacts
make build             # Build package with Poetry
make update-deps       # Update dependencies
```

### Docker Commands

```bash
# Build and run
make docker-build      # Build Docker image
make docker-run        # Run container interactively
make docker-up         # Start full stack with docker-compose
make docker-down       # Stop docker-compose services
make docker-logs-compose  # View docker-compose logs

# Development
make docker-shell      # Open bash shell in container
make docker-deploy     # Build and start (one command)

# Management
make docker-clean      # Remove container and image
make docker-ps         # List running containers
```

See `make help` for complete list of commands.

## Development Setup

### Prerequisites

- Python 3.12+
- Poetry installed globally
- Workspace virtual environment created

### Initial Setup

```bash
# 1. Ensure workspace venv exists
cd /Users/pralhad/work/src/pk-multi
make setup

# 2. Navigate to project
cd autobots-agents-bro

# 3. Install dependencies
poetry install
pip install -e .

# 4. Install pre-commit hooks
make install-hooks
```

### Running the Application

**Local Development:**

```bash
# Option 1: Using Makefile
make chainlit-dev

# Option 2: Direct script
bash sbin/run_bro.sh

# Option 3: Direct chainlit command
../.venv/bin/chainlit run src/autobots_agents_bro/usecase_ui.py --port 1337
```

Visit http://localhost:1337 to access the Chainlit UI.

**Docker Deployment:**

```bash
# Full stack with Langfuse observability
make docker-up

# Access:
# - BRO Chat: http://localhost:1337
# - Langfuse Web: http://localhost:3000
# - MinIO Console: http://localhost:9091
```

The docker-compose stack includes:
- **bro-chat**: Main Chainlit application
- **langfuse-web**: Langfuse UI for observability
- **langfuse-worker**: Background processing
- **postgres**: Database for Langfuse
- **clickhouse**: Analytics database
- **redis**: Caching layer
- **minio**: S3-compatible object storage

### Environment Configuration

Create `.env` file in project root:

```bash
# Required
GOOGLE_API_KEY=your_google_api_key

# Langfuse (optional - uses docker services by default)
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_ENABLED=true

# OAuth (optional)
OAUTH_GITHUB_CLIENT_ID=your_client_id
OAUTH_GITHUB_CLIENT_SECRET=your_client_secret
CHAINLIT_AUTH_SECRET=your_secret

# Debug
DEBUG=false
```

## Code Quality Standards

All configurations are in `pyproject.toml`:

### Ruff (Linter + Formatter)
- **Line length:** 100 characters (workspace standard)
- **Rules:** Comprehensive set including security checks, performance optimizations
- **Tests:** Relaxed rules for test files

### Pyright (Type Checker)
- **Mode:** `basic` (appropriate for complex Chainlit apps)
- **Paths:** Configured to find workspace dependencies
- **Python:** 3.12

### Pytest (Testing)
- **Paths:** `tests/` (unit, integration, e2e subdirectories)
- **Coverage:** Branch coverage enabled by default
- **Async:** Full async/await support with pytest-asyncio
- **Markers:** `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.unit`

### Pre-commit Hooks
- Ruff formatting and linting
- Pyright type checking (uses workspace venv)
- Pytest unit tests
- YAML/JSON/TOML validation
- Poetry lock file validation

## Architecture

### Agent Framework

Built on **Dynagent** from autobots-devtools-shared-lib:
- Multi-agent conversational workflows
- State management with LangGraph
- Google Gemini LLM integration
- Langfuse observability

### Document Store

Requirements are persisted using a file-based document store:
- JSON storage with metadata
- Versioning support
- Section-based organization
- Markdown export capability

### Batch Processing

Supports batch invocation of agents:
- Process multiple inputs in parallel
- Validation and error handling
- Progress tracking

## Testing

```bash
# Run all tests
make test

# Run specific test suite
make test-one TEST=tests/unit/
make test-one TEST=tests/integration/
make test-one TEST=tests/e2e/

# Run without coverage (faster)
make test-fast

# View coverage report
make test-cov
open htmlcov/index.html
```

**Test Organization:**
- `tests/unit/` - Fast, isolated unit tests
- `tests/integration/` - Tests with external dependencies
- `tests/e2e/` - Full end-to-end workflow tests

## Docker Deployment

The Dockerfile uses Poetry multi-stage build and requires **workspace root as build context**:

```bash
# Build from workspace root
cd /Users/pralhad/work/src/pk-multi
docker build -t autobots-agents-bro -f autobots-agents-bro/Dockerfile .

# Or use Makefile (handles context automatically)
cd autobots-agents-bro
make docker-build
```

**Build stages:**
1. **Builder:** Installs Poetry, builds autobots-devtools-shared-lib wheel, exports requirements
2. **Runtime:** Minimal Python image, installs dependencies, runs as non-root user

## Troubleshooting

**ModuleNotFoundError for autobots_devtools_shared_lib:**
```bash
# Ensure shared lib is installed in workspace venv
cd ../autobots-devtools-shared-lib
pip install -e .

# Then reinstall this project
cd ../autobots-agents-bro
pip install -e .
```

**Chainlit not found:**
```bash
# Ensure workspace venv is activated or use absolute path
source ../.venv/bin/activate
chainlit run src/autobots_agents_bro/usecase_ui.py --port 1337
```

**Docker build fails:**
```bash
# Ensure build context is workspace root
cd ..
docker build -t autobots-agents-bro -f autobots-agents-bro/Dockerfile .
```

**Tests fail with OAuth error:**
```bash
# Set required environment variables or skip OAuth tests
export OAUTH_GITHUB_CLIENT_ID=dummy
export OAUTH_GITHUB_CLIENT_SECRET=dummy
```

## Contributing

1. Run `make all-checks` before committing
2. All code must follow workspace standards (100 char line length, type annotations)
3. Tests must pass with coverage
4. Pre-commit hooks must pass

## License

[Specify license]

## Related Projects

- **autobots-devtools-shared-lib** - Shared library providing Dynagent framework, Chainlit UI, LLM tools
- **pk-multi workspace** - Multi-repo Python workspace with shared development environment
