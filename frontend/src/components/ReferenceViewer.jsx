import React, { useEffect, useMemo, useState } from "react";
import MarkdownIt from "markdown-it";
import DOMPurify from "dompurify";
import SearchIcon from "@mui/icons-material/Search";
import {
  Box,
  TextField,
  Button,
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
  Chip,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

const REF_TYPES = [
  "classes_md",
  "species_md",
  "monsters_md",
  "equipment_md",
  "magic_items_md",
  "spells_md",
  "tools_md",
  "weapons_md",
];

// Filter options
const SPELL_LEVELS = [
  { value: "", label: "Any Level" },
  { value: "0", label: "Cantrip" },
  { value: "1", label: "1st Level" },
  { value: "2", label: "2nd Level" },
  { value: "3", label: "3rd Level" },
  { value: "4", label: "4th Level" },
  { value: "5", label: "5th Level" },
  { value: "6", label: "6th Level" },
  { value: "7", label: "7th Level" },
  { value: "8", label: "8th Level" },
  { value: "9", label: "9th Level" },
];

const RARITIES = [
  { value: "", label: "Any Rarity" },
  { value: "Common", label: "Common" },
  { value: "Uncommon", label: "Uncommon" },
  { value: "Rare", label: "Rare" },
  { value: "Very Rare", label: "Very Rare" },
  { value: "Legendary", label: "Legendary" },
  { value: "Artifact", label: "Artifact" },
];

const SCHOOLS = [
  { value: "", label: "Any School" },
  { value: "Abjuration", label: "Abjuration" },
  { value: "Conjuration", label: "Conjuration" },
  { value: "Divination", label: "Divination" },
  { value: "Enchantment", label: "Enchantment" },
  { value: "Evocation", label: "Evocation" },
  { value: "Illusion", label: "Illusion" },
  { value: "Necromancy", label: "Necromancy" },
  { value: "Transmutation", label: "Transmutation" },
];

const CATEGORIES = [
  { value: "", label: "Any Category" },
  { value: "Weapon", label: "Weapon" },
  { value: "Armor", label: "Armor" },
  { value: "Potion", label: "Potion" },
  { value: "Ring", label: "Ring" },
  { value: "Rod", label: "Rod" },
  { value: "Scroll", label: "Scroll" },
  { value: "Staff", label: "Staff" },
  { value: "Wand", label: "Wand" },
  { value: "Wondrous item", label: "Wondrous Item" },
];

// Helper function to get spell level chip
const getSpellLevelChip = (level) => {
  if (level === undefined || level === null) return null;

  const levelInt = parseInt(level);
  const label = levelInt === 0 ? "Cantrip" : `Level ${levelInt}`;

  // Color gradient: cantrips are grey, low levels are blue, high levels are purple
  const getColor = () => {
    if (levelInt === 0) return "default";
    if (levelInt <= 2) return "primary";
    if (levelInt <= 5) return "info";
    if (levelInt <= 7) return "secondary";
    return "error";
  };

  return <Chip label={label} size="small" color={getColor()} sx={{ ml: 1 }} />;
};

// Helper function to get rarity chip
const getRarityChip = (rarity) => {
  if (!rarity) return null;

  // Color coding by rarity
  const getColor = () => {
    switch (rarity.toLowerCase()) {
      case "common":
        return "default";
      case "uncommon":
        return "success";
      case "rare":
        return "primary";
      case "very rare":
        return "secondary";
      case "legendary":
        return "warning";
      case "artifact":
        return "error";
      default:
        return "default";
    }
  };

  return <Chip label={rarity} size="small" color={getColor()} sx={{ ml: 1 }} />;
};

export default function ReferenceViewer({ refType: initialRefType = "class" }) {
  const [refType, setRefType] = useState(initialRefType);
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");

  // Metadata filters
  const [levelFilter, setLevelFilter] = useState("");
  const [rarityFilter, setRarityFilter] = useState("");
  const [schoolFilter, setSchoolFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");

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
        // Clear selection when changing reference types to show the list view
        setSelected(null);
      })
      .catch((e) => setError(String(e)))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [refType]);

  // Trigger a server-side sync from disk (imports markdown files into DB)
  const handleSyncFromDisk = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`/api/references/sync-from-disk`, {
        method: "POST",
      });
      if (!r.ok) throw new Error(`Sync failed: ${r.status}`);
      const data = await r.json();
      // After sync, re-fetch current ref_type
      const rep = await fetch(
        `/api/references/?ref_type=${encodeURIComponent(refType)}`
      );
      const list = await rep.json();
      setItems(list || []);
      // Clear selection after sync to show the list view
      setSelected(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const md = useMemo(
    () => new MarkdownIt({ html: true, linkify: true, typographer: true }),
    []
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let result = items;

    // Apply text search filter
    if (q) {
      result = result.filter(
        (it) =>
          (it.title || "").toLowerCase().includes(q) ||
          (it.key || "").toLowerCase().includes(q)
      );
    }

    // Apply metadata filters
    if (levelFilter !== "") {
      result = result.filter((it) => it.level === parseInt(levelFilter));
    }
    if (rarityFilter) {
      result = result.filter((it) => it.rarity === rarityFilter);
    }
    if (schoolFilter) {
      result = result.filter((it) => it.school === schoolFilter);
    }
    if (categoryFilter) {
      result = result.filter((it) => it.category === categoryFilter);
    }

    return result;
  }, [items, query, levelFilter, rarityFilter, schoolFilter, categoryFilter]);

  const renderedHtml = useMemo(() => {
    if (!selected) return "";
    const raw = selected.content || "*No content*";
    const rendered = md.render(raw);
    return DOMPurify.sanitize(rendered);
  }, [selected, md]);

  // Treat medium screens as desktop, but for very large displays (>= 1440px)
  // prefer the mobile/tabbed UX (tabbed list/detail) to avoid overly-wide
  // side-by-side layouts on ultra-wide monitors. We consider screens between
  // md and below 1440px as desktop (side-by-side), and 1440px+ as "mobile-like".
  const isMdUp = useMediaQuery((theme) => theme.breakpoints.up("md"));
  const isXlOrLarger = useMediaQuery("(min-width:1440px)");
  // isDesktop == true when md+ AND NOT ultra-wide (>=1440px)
  const isDesktop = isMdUp && !isXlOrLarger;
  const [mobileTab, setMobileTab] = useState(0); // 0=list, 1=detail

  // Monster search state (only shown for species)
  const [monsterQuery, setMonsterQuery] = useState("");
  const [monsterResults, setMonsterResults] = useState([]);
  const [monsterLoading, setMonsterLoading] = useState(false);

  const handleMonsterSearch = async () => {
    if (!monsterQuery || monsterQuery.trim().length === 0) return;
    setMonsterLoading(true);
    try {
      const q = encodeURIComponent(monsterQuery.trim());
      const r = await fetch(`/api/monsters/search?q=${q}&k=10`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      setMonsterResults(data || []);
    } catch (e) {
      setMonsterResults([]);
      console.error("Monster search failed", e);
      setError && setError(String(e));
    } finally {
      setMonsterLoading(false);
    }
  };

  // Keep internal refType state synchronized with the prop passed from parent.
  // When the parent (top-level tabs) changes the selected reference type,
  // update the local state so the component refetches the appropriate items.
  useEffect(() => {
    setRefType(initialRefType);
    // Reset filters when changing ref type
    setLevelFilter("");
    setRarityFilter("");
    setSchoolFilter("");
    setCategoryFilter("");
    // Reset mobile view back to the list on small screens when the top-level
    // reference type changes. We intentionally preserve the search `query`
    // so a user's filter remains when switching between types.
    if (!isDesktop) setMobileTab(0);
  }, [initialRefType, isDesktop]);

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

              {/* Metadata filters - show based on refType */}
              <Box sx={{ display: "flex", gap: 1, mb: 1, flexWrap: "wrap" }}>
                {/* Level filter for spells */}
                {refType === "spells_md" && (
                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Level</InputLabel>
                    <Select
                      value={levelFilter}
                      label="Level"
                      onChange={(e) => setLevelFilter(e.target.value)}
                    >
                      {SPELL_LEVELS.map((opt) => (
                        <MenuItem key={opt.value} value={opt.value}>
                          {opt.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}

                {/* School filter for spells */}
                {refType === "spells_md" && (
                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>School</InputLabel>
                    <Select
                      value={schoolFilter}
                      label="School"
                      onChange={(e) => setSchoolFilter(e.target.value)}
                    >
                      {SCHOOLS.map((opt) => (
                        <MenuItem key={opt.value} value={opt.value}>
                          {opt.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}

                {/* Rarity filter for magic items */}
                {refType === "magic_items_md" && (
                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Rarity</InputLabel>
                    <Select
                      value={rarityFilter}
                      label="Rarity"
                      onChange={(e) => setRarityFilter(e.target.value)}
                    >
                      {RARITIES.map((opt) => (
                        <MenuItem key={opt.value} value={opt.value}>
                          {opt.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}

                {/* Category filter for magic items */}
                {refType === "magic_items_md" && (
                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Category</InputLabel>
                    <Select
                      value={categoryFilter}
                      label="Category"
                      onChange={(e) => setCategoryFilter(e.target.value)}
                    >
                      {CATEGORIES.map((opt) => (
                        <MenuItem key={opt.value} value={opt.value}>
                          {opt.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}

                {/* Clear filters button */}
                {(levelFilter ||
                  rarityFilter ||
                  schoolFilter ||
                  categoryFilter) && (
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => {
                      setLevelFilter("");
                      setRarityFilter("");
                      setSchoolFilter("");
                      setCategoryFilter("");
                    }}
                  >
                    Clear Filters
                  </Button>
                )}
              </Box>

              <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
                {/* Monster search (species only) */}
                {refType === "species" && (
                  <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
                    <TextField
                      size="small"
                      placeholder="Search monsters"
                      value={monsterQuery}
                      onChange={(e) => setMonsterQuery(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleMonsterSearch();
                      }}
                    />
                    <Button
                      size="small"
                      onClick={handleMonsterSearch}
                      startIcon={<SearchIcon />}
                    >
                      Search
                    </Button>
                  </Box>
                )}
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
                    <ListItemText
                      primary={
                        <Box sx={{ display: "flex", alignItems: "center" }}>
                          {it.title}
                          {refType === "spells_md" &&
                            getSpellLevelChip(it.level)}
                          {refType === "magic_items_md" &&
                            getRarityChip(it.rarity)}
                        </Box>
                      }
                    />
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
                  {REF_TYPES.map((t) => {
                    // Convert folder names to user-friendly labels
                    const label = t
                      .replace(/_md$/, "")
                      .replace(/_/g, " ")
                      .split(" ")
                      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                      .join(" ");
                    return (
                      <MenuItem key={t} value={t}>
                        {label}
                      </MenuItem>
                    );
                  })}
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

            {/* Metadata filters - show based on refType */}
            <Box sx={{ display: "flex", gap: 1, mb: 1, flexWrap: "wrap" }}>
              {/* Level filter for spells */}
              {refType === "spells_md" && (
                <FormControl size="small" sx={{ minWidth: 110 }}>
                  <InputLabel>Level</InputLabel>
                  <Select
                    value={levelFilter}
                    label="Level"
                    onChange={(e) => setLevelFilter(e.target.value)}
                  >
                    {SPELL_LEVELS.map((opt) => (
                      <MenuItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}

              {/* School filter for spells */}
              {refType === "spells_md" && (
                <FormControl size="small" sx={{ minWidth: 110 }}>
                  <InputLabel>School</InputLabel>
                  <Select
                    value={schoolFilter}
                    label="School"
                    onChange={(e) => setSchoolFilter(e.target.value)}
                  >
                    {SCHOOLS.map((opt) => (
                      <MenuItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}

              {/* Rarity filter for magic items */}
              {refType === "magic_items_md" && (
                <FormControl size="small" sx={{ minWidth: 110 }}>
                  <InputLabel>Rarity</InputLabel>
                  <Select
                    value={rarityFilter}
                    label="Rarity"
                    onChange={(e) => setRarityFilter(e.target.value)}
                  >
                    {RARITIES.map((opt) => (
                      <MenuItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}

              {/* Category filter for magic items */}
              {refType === "magic_items_md" && (
                <FormControl size="small" sx={{ minWidth: 110 }}>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={categoryFilter}
                    label="Category"
                    onChange={(e) => setCategoryFilter(e.target.value)}
                  >
                    {CATEGORIES.map((opt) => (
                      <MenuItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}

              {/* Clear filters button */}
              {(levelFilter ||
                rarityFilter ||
                schoolFilter ||
                categoryFilter) && (
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    setLevelFilter("");
                    setRarityFilter("");
                    setSchoolFilter("");
                    setCategoryFilter("");
                  }}
                >
                  Clear
                </Button>
              )}
            </Box>

            <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
              <Button size="small" onClick={handleSyncFromDisk} sx={{ ml: 1 }}>
                Sync from disk
              </Button>
              <Button size="small" onClick={handleSyncFromDisk} sx={{ ml: 1 }}>
                Sync
              </Button>
            </Box>

            <Divider sx={{ mb: 1 }} />

            {loading && <Typography>Loading references...</Typography>}
            {error && (
              <Typography color="error">
                Error loading: {String(error)}
              </Typography>
            )}

            {/* If monsters_md and monster search results exist, show them first */}
            {refType === "monsters_md" && (
              <>
                <Typography variant="subtitle2" sx={{ mt: 1 }}>
                  Monster results
                </Typography>
                {monsterLoading && <Typography>Searching monsters…</Typography>}
                {monsterResults.length === 0 && !monsterLoading && (
                  <Typography color="text.secondary">
                    No monster results
                  </Typography>
                )}
                <List disablePadding>
                  {monsterResults.map((m) => (
                    <ListItemButton
                      key={m.id}
                      onClick={() => {
                        // Map monster into a reference-like object for detail pane
                        const refLike = {
                          id: m.id,
                          title: m.name,
                          content: `CR: ${m.cr || "—"}\nAC: ${
                            m.ac || "—"
                          }\nHP: ${m.hp || "—"}`,
                        };
                        setSelected(refLike);
                      }}
                    >
                      <ListItemText
                        primary={m.name}
                        secondary={`CR: ${m.cr || "—"} • HP: ${m.hp || "—"}`}
                      />
                    </ListItemButton>
                  ))}
                </List>
                <Divider sx={{ my: 1 }} />
              </>
            )}

            <List disablePadding>
              {filtered.map((it) => (
                <ListItemButton
                  key={it.id}
                  selected={selected && selected.id === it.id}
                  onClick={() => setSelected(it)}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: "flex", alignItems: "center" }}>
                        {it.title}
                        {refType === "spells_md" && getSpellLevelChip(it.level)}
                        {refType === "magic_items_md" &&
                          getRarityChip(it.rarity)}
                      </Box>
                    }
                  />
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
