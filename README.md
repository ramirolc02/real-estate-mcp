# Real Estate MCP Server

An MCP (Model Context Protocol) server that enables AI agents to search, retrieve, and generate content for real estate listings.

## Features

- **3 MCP Tools**: Search properties, get details, generate listing content
- **MCP Resource**: Daily digest of new listings (`realestate://listings/today`)
- **MCP Prompt**: Marketing email generator (`marketing-email`)
- **Bearer Token Authentication**: Secure API access
- **PostgreSQL Backend**: Efficient range queries, JSONB support
- **Async Architecture**: Non-blocking I/O throughout

## Why This Stack?

| Choice                | Rationale                                                                                                                                                                                         |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **PostgreSQL**        | Efficient range queries on price (`WHERE price BETWEEN x AND y`), JSONB for flexible features, mature async support, easily includes semantic search via pgvector, and can be deployed to AWS RDS |
| **Official MCP SDK**  | Spec-compliant, native resources/prompts, active maintenance by Anthropic                                                                                                                         |
| **uv**                | 10-100x faster than pip, reliable lockfiles, modern Python packaging                                                                                                                              |
| **FastMCP + FastAPI** | Decorator-based tools, SSE transport, familiar async patterns                                                                                                                                     |

## Quick Start

### Try the Live Demo (Fastest)

```bash
npx -y @modelcontextprotocol/inspector \
  --sse "https://real-estate-mcp-production.up.railway.app/mcp/sse" \
  --header "Authorization: Bearer demo-token-12345"
```

No setup needed! See [Live Demo](#live-demo) for more details.

### Using Docker Compose (Recommended)

```bash
# Clone and start
git clone <repo>
cd real-estate-mcp

# Configure environment (required)
cp .env.example .env
# Edit .env with your own values (API_TOKEN, database credentials, etc.)

# Start everything (db + seed + server)
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Test with MCP Inspector
npx -y @modelcontextprotocol/inspector --config mcp-inspector.json --server real-estate-mcp
```

This single command starts PostgreSQL, seeds the database with sample data, and launches the MCP server.

> ⚠️ **Important**: Never commit `.env` to version control. The `.env.example` file is a template with placeholder values.

### Local Development

```bash
# Prerequisites: uv, Docker (for PostgreSQL)

# 1. Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create environment
uv venv
source .venv/bin/activate

# 3. Install dependencies
uv sync --all-extras

# 4. Configure environment
cp .env.example .env
# Edit .env: set DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/realestate

# 5. Start PostgreSQL only
docker-compose up -d db

# 6. Seed database
uv run python -m src.db.seed

# 7. Run server
uv run uvicorn src.main:app --reload --port 8000

# 8. Lint/Format
uv run ruff check . --fix
uv run ruff format .

# 9. Run tests
uv run pytest -v
```

## API Authentication

All MCP endpoints require a Bearer token:

```bash
# Demo token for testing
Authorization: Bearer demo-token-12345
```

## Available MCP Tools

| Tool                       | Description            | Arguments                                  |
| -------------------------- | ---------------------- | ------------------------------------------ |
| `search_properties`        | Search with filters    | `city`, `min_price`, `max_price`, `status` |
| `get_property_details`     | Get full property data | `property_id` (required)                   |
| `generate_listing_content` | Generate SEO HTML      | `property_id`, `target_language`, `tone`   |

### Example Tool Calls

```json
// Search for apartments in Lisbon under €700k
{
  "name": "search_properties",
  "arguments": {
    "city": "Lisbon",
    "max_price": 700000,
    "status": "available"
  }
}

// Get property details
{
  "name": "get_property_details",
  "arguments": {
    "property_id": "11111111-1111-1111-1111-111111111111"
  }
}

// Generate listing content
{
  "name": "generate_listing_content",
  "arguments": {
    "property_id": "11111111-1111-1111-1111-111111111111",
    "target_language": "en",
    "tone": "luxury"
  }
}
```

## Available MCP Resources

| Resource URI                  | Description                             |
| ----------------------------- | --------------------------------------- |
| `realestate://listings/today` | Daily digest of new listings (last 24h) |

## Available MCP Prompts

| Prompt            | Description                       | Arguments     |
| ----------------- | --------------------------------- | ------------- |
| `marketing-email` | Generate property marketing email | `property_id` |

## Testing with MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) provides an interactive UI for testing:

### Using Config File (Recommended)

```bash
# Run inspector with the included config
npx -y @modelcontextprotocol/inspector --config mcp-inspector.json --server real-estate-mcp
```

This will launch the inspector at `http://localhost:6274` with authentication pre-configured.

### Manual Connection

Alternatively, connect manually via SSE:

```bash
npx -y @modelcontextprotocol/inspector sse http://localhost:8000/mcp/sse \
  --header "Authorization: Bearer demo-token-12345"
```

### CLI Mode for Scripting

Test tools programmatically:

```bash
# List all available tools
npx -y @modelcontextprotocol/inspector --cli \
  --config mcp-inspector.json --server real-estate-mcp \
  --method tools/list

# Search for properties in Lisbon
npx -y @modelcontextprotocol/inspector --cli \
  --config mcp-inspector.json --server real-estate-mcp \
  --method tools/call --tool-name search_properties \
  --tool-arg city=Lisbon --tool-arg status=available

# Get property details
npx -y @modelcontextprotocol/inspector --cli \
  --config mcp-inspector.json --server real-estate-mcp \
  --method tools/call --tool-name get_property_details \
  --tool-arg property_id=11111111-1111-1111-1111-111111111111
```

The inspector displays:

- All registered tools with their schemas
- Available resources
- Prompt templates
- Interactive testing interface
- Request/response history

## Live Demo

A public instance is deployed on Railway for testing:

|           |                                                             |
| --------- | ----------------------------------------------------------- |
| **URL**   | `https://real-estate-mcp-production.up.railway.app/mcp/sse` |
| **Token** | `demo-token-12345`                                          |

### Try it Now

```bash
# Connect via MCP Inspector (no installation required)
npx -y @modelcontextprotocol/inspector \
  --sse "https://real-estate-mcp-production.up.railway.app/mcp/sse" \
  --header "Authorization: Bearer demo-token-12345"
```

This opens an interactive UI at `http://localhost:6274` where you can:

- Browse all available tools, resources, and prompts
- Execute tool calls and see responses
- Test the full MCP protocol

### Configure Your MCP Client

Add this to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "real-estate": {
      "type": "sse",
      "url": "https://real-estate-mcp-production.up.railway.app/mcp/sse",
      "headers": {
        "Authorization": "Bearer demo-token-12345"
      }
    }
  }
}
```

No local setup required—just the URL and token!

## Deploy Your Own Instance (Railway)

1. Push to GitHub
2. Connect repo to [Railway](https://railway.app)
3. Add PostgreSQL plugin
4. Set environment variables in Railway Dashboard:
   - `API_TOKEN`: Your secret token
   - `DATABASE_URL`: Auto-configured by Railway
5. Deploy!

## Project Structure

```
real-estate-mcp/
├── src/
│   ├── main.py                 # FastAPI + FastMCP setup
│   ├── config.py               # Type-safe settings
│   ├── mcp_server.py           # MCP tools, resources, prompts
│   ├── auth.py                 # Bearer token middleware
│   ├── exceptions.py           # Custom MCP-friendly errors
│   ├── services/               # Business logic layer
│   ├── repositories/           # Data access layer
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic schemas
│   └── db/                     # Database session & seeding
├── templates/                  # Jinja2 templates
├── tests/                      # Unit tests
├── .env.example                # Environment template (copy to .env)
├── mcp-inspector.json          # MCP Inspector config (pre-configured auth)
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # Full stack orchestration
├── railway.toml                # Railway deployment config
└── pyproject.toml              # Dependencies & tooling
```

## Sample Properties

The database is seeded with 8 properties across:

- **Cities**: Lisbon, Porto, Cascais, Estoril, Sintra
- **Types**: Apartments, villas, penthouses, townhouses
- **Price Range**: €195k - €1.25M
- **Status**: Available and sold

## Environment Variables

These variables are only needed if you're **deploying/running the server yourself**. If you're connecting to an existing deployment, you only need the server URL and Bearer token.

| Variable            | Description               | Default                |
| ------------------- | ------------------------- | ---------------------- |
| `APP_NAME`          | Application name          | Real Estate MCP Server |
| `DEBUG`             | Enable debug mode         | false                  |
| `API_TOKEN`         | Bearer token for auth     | (required)             |
| `DATABASE_URL`      | PostgreSQL connection URL | (required)             |
| `POSTGRES_USER`     | Database username         | (for docker-compose)   |
| `POSTGRES_PASSWORD` | Database password         | (for docker-compose)   |
| `POSTGRES_DB`       | Database name             | (for docker-compose)   |
| `DB_POOL_SIZE`      | Connection pool size      | 5                      |
| `DB_MAX_OVERFLOW`   | Max overflow connections  | 10                     |

## License

MIT License - see LICENSE file for details.
