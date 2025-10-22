import React, { useEffect, useState } from "react";
import {
  Box,
  Button,
  TextField,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Checkbox,
  FormControlLabel,
  Typography,
  Paper,
  Divider,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";

export default function RagTesterPage() {
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("");
  const [availableModels, setAvailableModels] = useState([]);
  const [wantStructured, setWantStructured] = useState(false);
  const [parsedJson, setParsedJson] = useState(null);
  const [schemaText, setSchemaText] = useState("");
  const [schemaError, setSchemaError] = useState(null);
  const [query, setQuery] = useState("");
  const [k, setK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retrieved, setRetrieved] = useState([]);
  const [response, setResponse] = useState(null);

  const providers = ["groq", "openai", "google", "anthropic"];

  // Fetch provider models when provider changes (best-effort)
  useEffect(() => {
    let mounted = true;
    setAvailableModels([]);
    setModel("");
    setParsedJson(null);

    const fetchModels = async () => {
      try {
        const r = await fetch(
          `/api/llm/models?provider=${encodeURIComponent(provider)}`
        );
        if (!r.ok) return; // ignore silently and allow manual model entry
        const data = await r.json();
        if (!mounted) return;
        // Expecting data to be array of { id, name } or strings
        const list = Array.isArray(data)
          ? data.map((m) =>
              typeof m === "string"
                ? { id: m, name: m }
                : { id: m.id || m.name, name: m.name || m.id }
            )
          : [];
        setAvailableModels(list);
      } catch (e) {
        // ignore - backend may not expose models endpoint or network blocked
        console.debug("model fetch failed", e);
      }
    };

    fetchModels();
    return () => {
      mounted = false;
    };
  }, [provider]);

  const run = async () => {
    setError(null);
    setResponse(null);
    setRetrieved([]);
    if (!query || query.trim().length === 0) {
      setError("Please enter a query.");
      return;
    }

    setLoading(true);
    try {
      // 1) Retrieve top-k monster docs as demo (FAISS-first endpoint)
      const q = encodeURIComponent(query.trim());
      const r = await fetch(
        `/api/monsters/search?q=${q}&k=${encodeURIComponent(k)}`
      );
      if (!r.ok) throw new Error(`Retrieval failed: ${r.status}`);
      const docs = await r.json();
      setRetrieved(docs || []);

      // 2) Build a simple context prompt using top docs
      const context = (docs || [])
        .slice(0, k)
        .map(
          (d, i) =>
            `DOC ${i + 1}: ${d.name}\n${d.summary || d.description || ""}`
        )
        .join("\n\n");

      const prompt = `Use the following documents as context and answer the question concisely.\n\n${context}\n\nQuestion: ${query}`;

      // 3) Call the LLM endpoint
      // When structured output is requested, include a response_format hint
      const body = {
        provider,
        prompt,
        model: model || null,
        max_tokens: 800,
        temperature: 0.7,
      };

      // If a JSON schema was provided in the UI, validate and send it.
      if (schemaText && schemaText.trim().length > 0) {
        try {
          const parsedSchema = JSON.parse(schemaText);
          setSchemaError(null);
          // Provider-specific naming: Google uses response_schema, others use response_format
          if (provider === "google") {
            body.response_schema = parsedSchema;
          } else {
            body.response_format = parsedSchema;
          }
        } catch (e) {
          setSchemaError(String(e));
          throw new Error(`Invalid JSON schema: ${e.message}`);
        }
      } else if (wantStructured) {
        // Best-effort structured hint that many backends accept (schema-less JSON request)
        body.response_format = { type: "json" };
      }

      const gen = await fetch(`/api/llm/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!gen.ok) {
        const txt = await gen.text();
        throw new Error(`Generation failed: ${gen.status} ${txt}`);
      }

      const payload = await gen.json();
      setResponse(payload);

      // If the provider returned a JSON-ish content, try to parse it so we can
      // display structured output in a friendly way.
      setParsedJson(null);
      try {
        // payload.content may already be an object or a JSON string
        if (payload && payload.content) {
          if (typeof payload.content === "object") {
            setParsedJson(payload.content);
          } else if (typeof payload.content === "string") {
            const trimmed = payload.content.trim();
            if (
              (trimmed.startsWith("{") && trimmed.endsWith("}")) ||
              (trimmed.startsWith("[") && trimmed.endsWith("]"))
            ) {
              setParsedJson(JSON.parse(trimmed));
            }
          }
        }
      } catch (e) {
        // ignore JSON parse errors - show raw content below
        console.debug("Could not parse JSON from provider response", e);
      }
    } catch (e) {
      console.error(e);
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const estimateTokens = () => {
    // rough: 1 token ≈ 4 chars
    const promptLen = query ? query.length : 0;
    const contextLen = retrieved.reduce(
      (s, d) =>
        s + (d.name ? d.name.length : 0) + (d.summary ? d.summary.length : 0),
      0
    );
    const est = Math.max(1, Math.floor((promptLen + contextLen) / 4) + 100);
    return est;
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 2 }}>
        RAG Tester
      </Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2 }}>
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel id="provider-label">Provider</InputLabel>
            <Select
              labelId="provider-label"
              value={provider}
              label="Provider"
              onChange={(e) => setProvider(e.target.value)}
            >
              {providers.map((p) => (
                <MenuItem key={p} value={p}>
                  {p}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Model selector: prefer provider-discovered models when available */}
          {availableModels.length > 0 ? (
            <FormControl size="small" sx={{ minWidth: 220 }}>
              <InputLabel id="model-label">Model</InputLabel>
              <Select
                labelId="model-label"
                value={model}
                label="Model"
                onChange={(e) => setModel(e.target.value)}
              >
                <MenuItem value="">(default)</MenuItem>
                {availableModels.map((m) => (
                  <MenuItem key={m.id} value={m.id}>
                    {m.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          ) : (
            <TextField
              size="small"
              placeholder="Model (optional)"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            />
          )}

          <TextField
            size="small"
            type="number"
            label="k"
            value={k}
            onChange={(e) => setK(Number(e.target.value || 1))}
            sx={{ width: 88 }}
          />
        </Box>

        <TextField
          fullWidth
          multiline
          minRows={3}
          placeholder="Enter a question to test retrieval + generation"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          sx={{ mb: 2 }}
        />

        {/* Optional JSON schema for structured output */}
        <TextField
          fullWidth
          multiline
          minRows={3}
          placeholder='Optional JSON schema (e.g. { "type": "object", "properties": { "answer": { "type": "string" } } })'
          value={schemaText}
          onChange={(e) => setSchemaText(e.target.value)}
          sx={{ mb: 1 }}
          helperText={
            schemaError ||
            "Optional: provide a JSON schema to request structured output"
          }
          error={!!schemaError}
        />

        <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
          <Typography color="text.secondary" sx={{ mr: 1 }}>
            Est. prompt tokens: {estimateTokens()}
          </Typography>
          <Button variant="contained" onClick={run} disabled={loading}>
            Run
          </Button>
          <FormControlLabel
            control={
              <Checkbox
                checked={wantStructured}
                onChange={(e) => setWantStructured(e.target.checked)}
              />
            }
            label="Request JSON output"
          />
          <Button
            variant="outlined"
            onClick={() => {
              setQuery("");
              setRetrieved([]);
              setResponse(null);
              setError(null);
            }}
            disabled={loading}
          >
            Reset
          </Button>
          {loading && <CircularProgress size={24} sx={{ ml: 1 }} />}
        </Box>
      </Paper>

      <Box sx={{ display: "flex", gap: 2 }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6">Retrieved Documents</Typography>
          <Paper sx={{ p: 1, mt: 1, minHeight: 120 }}>
            {retrieved.length === 0 ? (
              <Typography color="text.secondary">No results</Typography>
            ) : (
              <List>
                {retrieved.map((d) => (
                  <ListItem key={d.id} alignItems="flex-start">
                    <ListItemText
                      primary={d.name || d.title}
                      secondary={d.summary || d.cr || d.description || ""}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Box>

        <Box sx={{ flex: 1 }}>
          <Typography variant="h6">LLM Response</Typography>
          <Paper sx={{ p: 2, mt: 1, minHeight: 120 }}>
            {error && (
              <Typography color="error" sx={{ mb: 1 }}>
                {error}
              </Typography>
            )}

            {response ? (
              <>
                <Typography variant="subtitle2" color="text.secondary">
                  Provider: {response.provider} • Model:{" "}
                  {response.model || "(default)"}
                </Typography>
                {response.generation_log &&
                  response.generation_log.narrative_provider && (
                    <Typography variant="caption" color="text.secondary">
                      Generated by: {response.generation_log.narrative_provider}
                    </Typography>
                  )}
                <Divider sx={{ my: 1 }} />
                {/* If parsedJson exists, render pretty JSON, otherwise show raw content */}
                {parsedJson ? (
                  <Box
                    component="pre"
                    sx={{
                      whiteSpace: "pre-wrap",
                      fontSize: "0.9rem",
                      overflow: "auto",
                    }}
                  >
                    {JSON.stringify(parsedJson, null, 2)}
                  </Box>
                ) : (
                  <Typography sx={{ whiteSpace: "pre-wrap" }}>
                    {response.content}
                  </Typography>
                )}
              </>
            ) : (
              <Typography color="text.secondary">No response yet</Typography>
            )}
          </Paper>
        </Box>
      </Box>
    </Box>
  );
}
