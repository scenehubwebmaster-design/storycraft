import React, { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  Box,
  TextField,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Typography,
  Divider,
} from "@mui/material";

const REF_TYPES = ["class", "species", "equipment", "other"];

export default function ReferenceViewer({ refType: initialRefType = "class" }) {
  const [refType, setRefType] = useState(initialRefType);
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);
    fetch(`/api/references/?ref_type=${encodeURIComponent(refType)}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        if (!mounted) return;
        setItems(data || []);
        setSelected((prev) => {
          if (prev && data && data.find((d) => d.id === prev.id)) return prev;
          return (data && data[0]) || null;
        });
      })
      .catch((e) => setError(String(e)))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [refType]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter(
      (it) =>
        (it.title || "").toLowerCase().includes(q) ||
        (it.key || "").toLowerCase().includes(q)
    );
  }, [items, query]);

  return (
    <Box sx={{ display: "flex", gap: 2 }}>
      <Paper sx={{ width: 360, maxHeight: 680, overflow: "auto", p: 2 }}>
        <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel id="ref-type-label">Type</InputLabel>
            <Select
              labelId="ref-type-label"
              value={refType}
              label="Type"
              onChange={(e) => setRefType(e.target.value)}
            >
              {REF_TYPES.map((t) => (
                <MenuItem key={t} value={t}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            size="small"
            placeholder="Search title or key"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            sx={{ flex: 1 }}
          />
        </Box>

        <Divider sx={{ mb: 1 }} />

        {loading && <Typography>Loading references...</Typography>}
        {error && (
          <Typography color="error">Error loading: {String(error)}</Typography>
        )}

        <List disablePadding>
          {filtered.map((it) => (
            <ListItemButton
              key={it.id}
              selected={selected && selected.id === it.id}
              onClick={() => setSelected(it)}
            >
              <ListItemText primary={it.title} secondary={it.key} />
            </ListItemButton>
          ))}
        </List>
      </Paper>

      <Paper sx={{ flexGrow: 1, p: 3, maxHeight: 680, overflow: "auto" }}>
        {selected ? (
          <div>
            <Typography variant="h5" gutterBottom>
              {selected.title}
            </Typography>
            <ReactMarkdown>{selected.content || "*No content*"}</ReactMarkdown>
          </div>
        ) : (
          <Typography color="text.secondary">No reference selected</Typography>
        )}
      </Paper>
    </Box>
  );
}
