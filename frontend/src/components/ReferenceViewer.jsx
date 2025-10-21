import React, { useEffect, useMemo, useState } from "react";
import MarkdownIt from "markdown-it";
import DOMPurify from "dompurify";
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
  Grid,
  TableContainer,
  Tabs,
  Tab,
  useMediaQuery,
  IconButton,
  Stack,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

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

  const md = useMemo(
    () => new MarkdownIt({ html: true, linkify: true, typographer: true }),
    []
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter(
      (it) =>
        (it.title || "").toLowerCase().includes(q) ||
        (it.key || "").toLowerCase().includes(q)
    );
  }, [items, query]);

  const renderedHtml = useMemo(() => {
    if (!selected) return "";
    const raw = selected.content || "*No content*";
    const rendered = md.render(raw);
    return DOMPurify.sanitize(rendered);
  }, [selected, md]);

  const isWide = useMediaQuery((theme) => theme.breakpoints.up("md"));
  const isTall = useMediaQuery("(min-height:1080px)");
  const isDesktop = isWide && isTall;
  const [mobileTab, setMobileTab] = useState(0); // 0=list, 1=detail

  // Heights used to make the left/right columns scroll independently.
  // On desktop we reserve some space for app chrome / padding; adjust if needed.
  const desktopContentHeight = isDesktop ? "calc(100vh - 160px)" : "auto";
  // Mobile content area (tabs + headers take space) - keep content scrollable inside the pane.
  const mobileContentHeight = !isDesktop ? "calc(100vh - 140px)" : "auto";

  useEffect(() => {
    // Keep mobileTab in sync: if selection changes and we are on mobile, show details
    if (!isDesktop && selected) setMobileTab(1);
  }, [selected, isDesktop]);

  // Layout: side-by-side Grid on md+; tabbed list/detail on small screens
  if (!isDesktop) {
    return (
      <Paper
        sx={{
          width: "100%",
          height: "100vh",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Tabs
          value={mobileTab}
          onChange={(e, v) => setMobileTab(v)}
          variant="fullWidth"
        >
          <Tab label={`List (${filtered.length})`} />
          <Tab label="Details" disabled={!selected} />
        </Tabs>

        {/* Content area: fills remaining height and scrolls internally so both tabs scroll */}
        <Box sx={{ flex: 1, overflow: "auto" }}>
          {mobileTab === 0 && (
            <Box sx={{ p: 2 }}>
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
                <Typography color="error">
                  Error loading: {String(error)}
                </Typography>
              )}

              <List disablePadding>
                {filtered.map((it) => (
                  <ListItemButton
                    key={it.id}
                    selected={selected && selected.id === it.id}
                    onClick={() => {
                      setSelected(it);
                      setMobileTab(1);
                    }}
                  >
                    <ListItemText primary={it.title} secondary={it.key} />
                  </ListItemButton>
                ))}
              </List>
            </Box>
          )}

          {mobileTab === 1 && (
            <Box sx={{ p: 2 }}>
              <Stack
                direction="row"
                alignItems="center"
                spacing={1}
                sx={{ mb: 1 }}
              >
                <IconButton onClick={() => setMobileTab(0)} size="small">
                  <ArrowBackIcon />
                </IconButton>
                <Typography variant="h6">
                  {selected ? selected.title : "Details"}
                </Typography>
              </Stack>

              {selected ? (
                <Box
                  sx={{
                    px: 1,
                    "& img": {
                      maxWidth: "100%",
                      height: "auto",
                      display: "block",
                      margin: "8px 0",
                    },
                    "& pre": {
                      fontFamily: "monospace",
                      fontSize: "0.9rem",
                      padding: 12,
                      background: "rgba(0,0,0,0.04)",
                      borderRadius: 4,
                      overflow: "auto",
                    },
                    "& code": {
                      fontFamily: "monospace",
                      fontSize: "0.85rem",
                      background: "rgba(0,0,0,0.02)",
                      padding: "2px 6px",
                      borderRadius: 4,
                    },
                    "& table": {
                      width: "100%",
                      borderCollapse: "separate",
                      borderSpacing: 0,
                      border: "1px solid rgba(0,0,0,0.08)",
                      borderRadius: 6,
                      overflow: "hidden",
                    },
                    "& thead th": {
                      position: "sticky",
                      top: 0,
                      background: (theme) => theme.palette.background.paper,
                      zIndex: 2,
                      boxShadow: "inset 0 -1px 0 rgba(0,0,0,0.06)",
                    },
                    "& th, & td": {
                      textAlign: "left",
                      padding: "12px 14px",
                      borderBottom: "1px solid rgba(0,0,0,0.06)",
                      verticalAlign: "top",
                    },
                    "& tbody tr:nth-of-type(odd)": {
                      background: (theme) => theme.palette.action.hover,
                    },
                    "& tbody tr:hover": {
                      background: (theme) => theme.palette.action.selected,
                    },
                  }}
                >
                  <div dangerouslySetInnerHTML={{ __html: renderedHtml }} />
                </Box>
              ) : (
                <Typography color="text.secondary">
                  No reference selected
                </Typography>
              )}
            </Box>
          )}
        </Box>
      </Paper>
    );
  }

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={4} lg={3}>
        <Paper
          sx={{
            width: "100%",
            height: desktopContentHeight,
            overflow: "hidden",
            p: 2,
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Box sx={{ height: "100%", overflow: "auto" }}>
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
              <Typography color="error">
                Error loading: {String(error)}
              </Typography>
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
          </Box>
        </Paper>
      </Grid>

      <Grid item xs={12} md={8} lg={9}>
        <Paper sx={{ p: 3, height: desktopContentHeight, overflow: "hidden" }}>
          <Box sx={{ height: "100%", overflow: "auto" }}>
            {selected ? (
              <>
                <Typography variant="h5" gutterBottom>
                  {selected.title}
                </Typography>

                {/* Use TableContainer when markdown contains tables to mimic MUI table scrolling behavior */}
                {renderedHtml.includes("<table") ? (
                  <TableContainer component={Paper} sx={{ overflowX: "auto" }}>
                    <Box
                      sx={{
                        p: 2,
                        "& img": {
                          maxWidth: "100%",
                          height: "auto",
                          display: "block",
                          margin: "8px 0",
                        },
                        "& pre": {
                          fontFamily: "monospace",
                          fontSize: "0.9rem",
                          padding: 12,
                          background: "rgba(0,0,0,0.04)",
                          borderRadius: 4,
                          overflow: "auto",
                        },
                        "& code": {
                          fontFamily: "monospace",
                          fontSize: "0.85rem",
                          background: "rgba(0,0,0,0.02)",
                          padding: "2px 6px",
                          borderRadius: 4,
                        },
                        "& table": {
                          minWidth: 650,
                          width: "100%",
                          borderCollapse: "separate",
                          borderSpacing: 0,
                          border: "1px solid rgba(0,0,0,0.08)",
                          borderRadius: 6,
                          overflow: "hidden",
                        },
                        "& thead th": {
                          position: "sticky",
                          top: 0,
                          background: (theme) => theme.palette.background.paper,
                          zIndex: 2,
                          boxShadow: "inset 0 -1px 0 rgba(0,0,0,0.06)",
                        },
                        "& th, & td": {
                          textAlign: "left",
                          padding: "12px 14px",
                          borderBottom: "1px solid rgba(0,0,0,0.06)",
                          verticalAlign: "top",
                        },
                        "& tbody tr:nth-of-type(odd)": {
                          background: (theme) => theme.palette.action.hover,
                        },
                        "& tbody tr:hover": {
                          background: (theme) => theme.palette.action.selected,
                        },
                      }}
                      dangerouslySetInnerHTML={{ __html: renderedHtml }}
                    />
                  </TableContainer>
                ) : (
                  <Box
                    sx={{
                      px: 1,
                      "& img": {
                        maxWidth: "100%",
                        height: "auto",
                        display: "block",
                        margin: "8px 0",
                      },
                      "& pre": {
                        fontFamily: "monospace",
                        fontSize: "0.9rem",
                        padding: 12,
                        background: "rgba(0,0,0,0.04)",
                        borderRadius: 4,
                        overflow: "auto",
                      },
                      "& code": {
                        fontFamily: "monospace",
                        fontSize: "0.85rem",
                        background: "rgba(0,0,0,0.02)",
                        padding: "2px 6px",
                        borderRadius: 4,
                      },
                      "& table": {
                        width: "100%",
                        borderCollapse: "separate",
                        borderSpacing: 0,
                        border: "1px solid rgba(0,0,0,0.08)",
                        borderRadius: 6,
                        overflow: "hidden",
                      },
                      "& thead th": {
                        position: "sticky",
                        top: 0,
                        background: (theme) => theme.palette.background.paper,
                        zIndex: 2,
                        boxShadow: "inset 0 -1px 0 rgba(0,0,0,0.06)",
                      },
                      "& th, & td": {
                        textAlign: "left",
                        padding: "12px 14px",
                        borderBottom: "1px solid rgba(0,0,0,0.06)",
                        verticalAlign: "top",
                      },
                      "& tbody tr:nth-of-type(odd)": {
                        background: (theme) => theme.palette.action.hover,
                      },
                      "& tbody tr:hover": {
                        background: (theme) => theme.palette.action.selected,
                      },
                    }}
                  >
                    <div dangerouslySetInnerHTML={{ __html: renderedHtml }} />
                  </Box>
                )}
              </>
            ) : (
              <Typography color="text.secondary">
                No reference selected
              </Typography>
            )}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
}
