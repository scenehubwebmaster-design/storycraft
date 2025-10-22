# D&D MCP Proxy Server

Node.js HTTP proxy server that bridges Python FastAPI backend with D&D MCP server.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd scripts
npm install
```

### 2. Start the Proxy Server

```bash
node mcp_proxy_server.js
```

The server will start on **port 3001** by default.

### 3. Test the Integration

In a separate terminal:

```bash
cd scripts
python test_dnd_mcp_integration.py
```

## 📋 Available Endpoints

### Health & Status

- `GET /health` - Check proxy server status
- `GET /api/health` - Check D&D 5e API health

### Search & Query

- `POST /api/search` - Search all D&D content

  ```json
  { "query": "fireball" }
  ```

- `GET /api/spell/:name` - Get spell details
- `GET /api/monster/:name` - Get monster details

### Filtering

- `GET /api/spells?min_level=0&max_level=9&school=evocation` - Filter spells
- `GET /api/monsters?min_cr=0&max_cr=5` - Find monsters by CR
- `GET /api/equipment?max_cost=10&cost_unit=gp` - Search equipment by cost

### Verification

- `POST /api/verify` - Verify D&D statement
  ```json
  {
    "statement": "Fireball is a 3rd-level evocation spell",
    "category": "spells"
  }
  ```

## 🔧 Configuration

### Environment Variables

- `MCP_PROXY_PORT` - Server port (default: 3001)

### MCP Server Path

Edit `mcp_proxy_server.js` if your DnD MCP server is in a different location:

```javascript
const transport = new StdioClientTransport({
  command: "uv",
  args: ["--directory", "E:\\dnd-mcp", "run", "dnd_mcp_server.py"],
});
```

## 🐛 Troubleshooting

### Server won't start

**Error**: `Cannot find module '@modelcontextprotocol/sdk'`

**Solution**: Run `npm install` in the `scripts` directory

### Connection refused

**Error**: `Failed to connect to MCP proxy: ECONNREFUSED`

**Solution**: Make sure the proxy server is running on port 3001

### MCP client not connected

**Error**: `MCP client not connected`

**Solution**:

1. Check that the DnD MCP server path is correct
2. Verify `uv` is installed and in PATH
3. Check that E:\dnd-mcp exists and has dnd_mcp_server.py

## 📊 Architecture

```
┌─────────────────────────────────────────────┐
│          Python FastAPI Backend             │
│    (backend/services/dnd_mcp_client.py)     │
└─────────────────┬───────────────────────────┘
                  │ HTTP Requests
                  │ (localhost:3001)
┌─────────────────▼───────────────────────────┐
│         MCP Proxy Server (Node.js)          │
│       (scripts/mcp_proxy_server.js)         │
│  • Express HTTP server                      │
│  • Request/response translation             │
│  • Error handling                           │
└─────────────────┬───────────────────────────┘
                  │ stdio
┌─────────────────▼───────────────────────────┐
│         DnD MCP Server (Python)             │
│         (E:\dnd-mcp\dnd_mcp_server.py)      │
│  • Connects to D&D 5e API                   │
│  • Official D&D content                     │
│  • Caching & prefetching                    │
└─────────────────────────────────────────────┘
```

## 📝 Example Usage

### Python Client

```python
from backend.services.dnd_mcp_client import DndMcpClient

async with DndMcpClient() as client:
    # Search for content
    results = await client.search_all("fireball")

    # Get spell details
    spell = await client.get_spell("fireball")

    # Find monsters
    monsters = await client.find_monsters_by_cr(0, 5)

    # Filter spells
    cantrips = await client.filter_spells_by_level(0, 0)
```

### HTTP API (curl)

```bash
# Search
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "fireball"}'

# Get spell
curl http://localhost:3001/api/spell/fireball

# Filter spells
curl "http://localhost:3001/api/spells?min_level=1&max_level=3&school=evocation"
```

## 🎯 Next Steps

1. ✅ Phase 1: MCP Proxy & Python Client (COMPLETE)
2. ⏳ Phase 2: D&D Knowledge Markdown Files
3. ⏳ Phase 3: Narrative Engine Integration
4. ⏳ Phase 4: DM Chat Handler Enhancement
5. ⏳ Phase 5: API Endpoints
6. ⏳ Phase 6: Frontend Components

See `DND_MCP_INTEGRATION_PLAN.md` for full roadmap.
