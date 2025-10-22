/**
 * MCP Proxy Server
 *
 * Bridges Node.js MCP server with Python FastAPI backend.
 * Accepts HTTP requests and forwards to MCP stdio server.
 *
 * Architecture:
 * - Express HTTP server on port 3001
 * - Communicates with D&D MCP server via stdio
 * - Provides REST endpoints for Python backend
 * - Handles error cases and retries
 */

const express = require("express");
const cors = require("cors");
const { Client } = require("@modelcontextprotocol/sdk/client/index.js");
const {
  StdioClientTransport,
} = require("@modelcontextprotocol/sdk/client/stdio.js");

const app = express();
const PORT = process.env.MCP_PROXY_PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// MCP client instance
let mcpClient = null;
let isConnected = false;
let connectionError = null;

/**
 * Initialize MCP client connection
 */
async function initializeMCP() {
  try {
    console.log("Initializing MCP client connection...");

    const transport = new StdioClientTransport({
      command: "uv",
      args: ["--directory", "E:\\dnd-mcp", "run", "dnd_mcp_server.py"],
      env: process.env,
    });

    mcpClient = new Client(
      {
        name: "dnd-proxy",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    await mcpClient.connect(transport);
    isConnected = true;
    connectionError = null;

    console.log("✅ MCP client connected successfully");

    // List available tools
    const toolsResult = await mcpClient.listTools();
    console.log(`📋 Available tools: ${toolsResult.tools.length}`);
    toolsResult.tools.forEach((tool) => {
      console.log(`  - ${tool.name}`);
    });
  } catch (error) {
    isConnected = false;
    connectionError = error.message;
    console.error("❌ Failed to initialize MCP client:", error);
    throw error;
  }
}

/**
 * Health check endpoint
 */
app.get("/health", (req, res) => {
  res.json({
    status: isConnected ? "connected" : "disconnected",
    error: connectionError,
    timestamp: new Date().toISOString(),
  });
});

/**
 * Check API health
 */
app.get("/api/health", async (req, res) => {
  try {
    if (!isConnected) {
      return res.status(503).json({
        error: "MCP client not connected",
        detail: connectionError,
      });
    }

    const result = await mcpClient.callTool("check_api_health", {});
    res.json(result);
  } catch (error) {
    console.error("Error checking API health:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Search all D&D categories
 * POST /api/search
 * Body: { query: string }
 */
app.post("/api/search", async (req, res) => {
  try {
    if (!isConnected) {
      return res.status(503).json({
        error: "MCP client not connected",
        detail: connectionError,
      });
    }

    const { query } = req.body;

    if (!query || query.trim().length === 0) {
      return res.status(400).json({ error: "Query parameter is required" });
    }

    console.log(`🔍 Searching for: "${query}"`);

    const result = await mcpClient.callTool("search_all_categories", { query });

    console.log(
      `✅ Found ${result.content?.[0]?.text ? "results" : "no results"}`
    );

    res.json(result);
  } catch (error) {
    console.error("Error searching D&D content:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get spell by name
 * GET /api/spell/:name
 */
app.get("/api/spell/:name", async (req, res) => {
  try {
    if (!isConnected) {
      return res.status(503).json({
        error: "MCP client not connected",
        detail: connectionError,
      });
    }

    const { name } = req.params;

    console.log(`🔮 Looking up spell: "${name}"`);

    // Search for the spell
    const result = await mcpClient.callTool("search_all_categories", {
      query: name,
    });

    res.json(result);
  } catch (error) {
    console.error("Error fetching spell:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get monster by name
 * GET /api/monster/:name
 */
app.get("/api/monster/:name", async (req, res) => {
  try {
    if (!isConnected) {
      return res.status(503).json({
        error: "MCP client not connected",
        detail: connectionError,
      });
    }

    const { name } = req.params;

    console.log(`👹 Looking up monster: "${name}"`);

    const result = await mcpClient.callTool("search_all_categories", {
      query: name,
    });

    res.json(result);
  } catch (error) {
    console.error("Error fetching monster:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Filter spells by level
 * GET /api/spells?min_level=0&max_level=9&school=evocation
 */
app.get("/api/spells", async (req, res) => {
  try {
    if (!isConnected) {
      return res.status(503).json({
        error: "MCP client not connected",
        detail: connectionError,
      });
    }

    const { min_level = 0, max_level = 9, school = null } = req.query;

    console.log(
      `📚 Filtering spells: level ${min_level}-${max_level}${
        school ? `, school: ${school}` : ""
      }`
    );

    const result = await mcpClient.callTool("filter_spells_by_level", {
      min_level: parseInt(min_level),
      max_level: parseInt(max_level),
      school: school || undefined,
    });

    res.json(result);
  } catch (error) {
    console.error("Error filtering spells:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Find monsters by challenge rating
 * GET /api/monsters?min_cr=0&max_cr=5
 */
app.get("/api/monsters", async (req, res) => {
  try {
    if (!isConnected) {
      return res.status(503).json({
        error: "MCP client not connected",
        detail: connectionError,
      });
    }

    const { min_cr = 0, max_cr = 30 } = req.query;

    console.log(`🐉 Finding monsters: CR ${min_cr}-${max_cr}`);

    const result = await mcpClient.callTool(
      "find_monsters_by_challenge_rating",
      {
        min_cr: parseFloat(min_cr),
        max_cr: parseFloat(max_cr),
      }
    );

    res.json(result);
  } catch (error) {
    console.error("Error finding monsters:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get equipment by cost
 * GET /api/equipment?max_cost=10&cost_unit=gp
 */
app.get("/api/equipment", async (req, res) => {
  try {
    if (!isConnected) {
      return res.status(503).json({
        error: "MCP client not connected",
        detail: connectionError,
      });
    }

    const { max_cost = 100, cost_unit = "gp" } = req.query;

    console.log(`⚔️ Finding equipment: max ${max_cost} ${cost_unit}`);

    const result = await mcpClient.callTool("search_equipment_by_cost", {
      max_cost: parseFloat(max_cost),
      cost_unit,
    });

    res.json(result);
  } catch (error) {
    console.error("Error finding equipment:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Verify D&D statement
 * POST /api/verify
 * Body: { statement: string, category?: string }
 */
app.post("/api/verify", async (req, res) => {
  try {
    if (!isConnected) {
      return res.status(503).json({
        error: "MCP client not connected",
        detail: connectionError,
      });
    }

    const { statement, category = null } = req.body;

    if (!statement || statement.trim().length === 0) {
      return res.status(400).json({ error: "Statement parameter is required" });
    }

    console.log(`✓ Verifying: "${statement}"`);

    const result = await mcpClient.callTool("verify_with_api", {
      statement,
      category: category || undefined,
    });

    res.json(result);
  } catch (error) {
    console.error("Error verifying statement:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Error handler
 */
app.use((err, req, res, next) => {
  console.error("Unhandled error:", err);
  res.status(500).json({ error: "Internal server error", detail: err.message });
});

/**
 * Start server
 */
async function start() {
  try {
    // Initialize MCP connection
    await initializeMCP();

    // Start HTTP server
    app.listen(PORT, () => {
      console.log(`\n🚀 MCP Proxy Server running on port ${PORT}`);
      console.log(`📍 Health check: http://localhost:${PORT}/health`);
      console.log(`🎲 D&D API: http://localhost:${PORT}/api/search`);
      console.log("\nEndpoints:");
      console.log("  GET  /health          - Server health check");
      console.log("  GET  /api/health      - D&D API health check");
      console.log("  POST /api/search      - Search all D&D content");
      console.log("  GET  /api/spell/:name - Get spell details");
      console.log("  GET  /api/monster/:name - Get monster details");
      console.log("  GET  /api/spells      - Filter spells by level");
      console.log("  GET  /api/monsters    - Find monsters by CR");
      console.log("  GET  /api/equipment   - Find equipment by cost");
      console.log("  POST /api/verify      - Verify D&D statement");
      console.log("\n✨ Ready to serve D&D 5e content!\n");
    });
  } catch (error) {
    console.error("❌ Failed to start server:", error);
    process.exit(1);
  }
}

/**
 * Graceful shutdown
 */
process.on("SIGINT", () => {
  console.log("\n👋 Shutting down gracefully...");
  if (mcpClient) {
    mcpClient.close();
  }
  process.exit(0);
});

process.on("SIGTERM", () => {
  console.log("\n👋 Shutting down gracefully...");
  if (mcpClient) {
    mcpClient.close();
  }
  process.exit(0);
});

// Start the server
start();
