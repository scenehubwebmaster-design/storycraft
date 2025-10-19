import { Link, useNavigate, useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";
import {
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import StructuredWorldDisplay from "../components/StructuredWorldDisplay";
import { API_URL } from "../config/api";
import ImageLightbox from "../components/ImageLightbox";
import WorldMapOverlay from "../components/WorldMapOverlay";
import MapLeafletOverlay from "../components/MapLeafletOverlay";
import WorldImageMapOverlay from "../components/WorldImageMapOverlay";
import POIGenerationDialog from "../components/POIGenerationDialog";
import RegionGenerateDialog from "../components/RegionGenerateDialog";
import SaveRegionDialog from "../components/SaveRegionDialog";

export default function WorldDetailPage() {
  const { worldId } = useParams();
  const navigate = useNavigate();
  const [world, setWorld] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxSrc, setLightboxSrc] = useState(null);
  const [lightboxAlt, setLightboxAlt] = useState(null);
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    loadWorld();
    loadLocations();
  }, [worldId]);

  const loadWorld = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/worlds/${worldId}`);
      setWorld(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load world");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadLocations = async () => {
    try {
      const resp = await axios.get(`${API_URL}/api/locations/`, {
        params: { world_id: worldId },
      });
      setLocations(resp.data || []);
    } catch (e) {
      // If endpoint missing, try to use world.locations returned in world
      console.debug(
        "Failed to load locations separately, falling back to world.locations if present",
        e
      );
    }
  };

  // Generation and POI modal handlers
  const [poiDialog, setPoiDialog] = useState({ open: false, poi: null });
  const [isGenerating, setIsGenerating] = useState(false);
  const [tileProvider, setTileProvider] = useState("osm");
  const [seeding, setSeeding] = useState(false);
  const [seedProgress, setSeedProgress] = useState({ done: 0, total: 0 });
  const [autoPortraits, setAutoPortraits] = useState(false);
  const [regionDialog, setRegionDialog] = useState({
    open: false,
    bounds: null,
  });
  const [saveRegionDialog, setSaveRegionDialog] = useState({ open: false });
  const [croppedRegionImage, setCroppedRegionImage] = useState(null);
  const [suggestedCoords, setSuggestedCoords] = useState(null);
  const [regionContext, setRegionContext] = useState(null);
  const [saveDialogMeta, setSaveDialogMeta] = useState({
    isGenerating: false,
    provider: null,
    promptUsed: null,
    generationError: null,
  });
  const [croppedImageDimensions, setCroppedImageDimensions] = useState(null);
  const [imageNaturalSize, setImageNaturalSize] = useState(null);

  const TILE_PROVIDERS = {
    osm: {
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attribution: "&copy; OpenStreetMap contributors",
    },
    stamen_terrain: {
      url: "https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
      attribution:
        "Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap",
    },
    stamen_watercolor: {
      url: "https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg",
      attribution:
        "Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap",
    },
    carto_dark: {
      url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
      attribution: "&copy; CartoDB & OpenStreetMap",
    },
  };

  const handleGenerateLandscape = async () => {
    if (!world) return;
    setIsGenerating(true);
    try {
      const resp = await axios.post(
        `${API_URL}/api/generate/world/generate-landscape/`,
        {
          name: world.name,
          description: world.description || "",
        }
      );
      const { image_base64, prompt } = resp.data || {};
      if (image_base64) {
        setLightboxSrc(`data:image/png;base64,${image_base64}`);
        setLightboxAlt("Generated Landscape");
        setLightboxOpen(true);
        const save = window.confirm(
          "Save generated landscape to this world? (OK = save, Cancel = discard)"
        );
        if (save) {
          await axios.post(`${API_URL}/api/generate/world/structured/save/`, {
            world_id: world.id,
            world_image: image_base64,
            image_prompt: prompt,
          });
          await loadWorld();
        }
      } else {
        alert("No image returned from generation endpoint.");
      }
    } catch (err) {
      console.error(err);
      alert("Generation failed. Check server logs.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleMarkerClick = (m) => {
    setPoiDialog({ open: true, poi: m });
  };

  const handleRegionCreated = (bounds, ctx) => {
    // ctx is expected to be an object like { isImage: boolean, imageSize: {x,y}?, layer }
    setRegionContext(ctx || {});
    setRegionDialog({ open: true, bounds });
  };

  const handleRegionGenerate = async ({
    prompt,
    regionBounds,
    useCropAndGenerate = false,
    provider = "stablediffusion",
  }) => {
    try {
      const ctx = regionContext || {};
      if (!ctx.isImage) {
        // Geospatial flow: call image generation and show save dialog
        const sw = regionBounds._southWest || regionBounds.getSouthWest();
        const ne = regionBounds._northEast || regionBounds.getNorthEast();
        const centerLat = (sw.lat + ne.lat) / 2;
        const centerLng = (sw.lng + ne.lng) / 2;

        const resp = await axios.post(
          `${API_URL}/api/generate/location/generate-image/`,
          {
            location_name: `Region ${centerLat.toFixed(2)},${centerLng.toFixed(
              2
            )}`,
            location_type: "region",
            description: prompt,
          }
        );
        const image_base64 = resp.data?.image_base64;
        if (image_base64) {
          setCroppedRegionImage(image_base64);
          setSuggestedCoords(
            `${centerLat.toFixed(6)}, ${centerLng.toFixed(6)}`
          );
          setSaveDialogMeta({
            isGenerating: false,
            provider: null,
            promptUsed: null,
            generationError: null,
          });
          setSaveRegionDialog({ open: true });
        }
        return;
      }

      // Image overlay flow: convert pixel bounds to percent bounds
      const sw = regionBounds._southWest || regionBounds.getSouthWest();
      const ne = regionBounds._northEast || regionBounds.getNorthEast();
      const x1 = Math.min(sw.lng, ne.lng);
      const x2 = Math.max(sw.lng, ne.lng);
      const y1 = Math.min(sw.lat, ne.lat);
      const y2 = Math.max(sw.lat, ne.lat);

      let percentBounds;
      if (ctx.imageSize) {
        let imgW = null;
        let imgH = null;
        if (
          typeof ctx.imageSize.width === "number" &&
          typeof ctx.imageSize.height === "number"
        ) {
          imgW = ctx.imageSize.width;
          imgH = ctx.imageSize.height;
        } else if (
          typeof ctx.imageSize.x === "number" &&
          typeof ctx.imageSize.y === "number"
        ) {
          imgW = ctx.imageSize.x;
          imgH = ctx.imageSize.y;
        }

        if (imgW && imgH) {
          percentBounds = {
            x1: (x1 / imgW) * 100,
            y1: (y1 / imgH) * 100,
            x2: (x2 / imgW) * 100,
            y2: (y2 / imgH) * 100,
          };
        } else {
          percentBounds = { x1, y1, x2, y2 };
        }
      } else {
        percentBounds = { x1, y1, x2, y2 };
      }

      if (useCropAndGenerate) {
        // indicate generation in progress and open dialog immediately
        setSaveDialogMeta({
          isGenerating: true,
          provider,
          promptUsed: prompt,
          generationError: null,
        });
        setSaveRegionDialog({ open: true });

        try {
          const genResp = await axios.post(
            `${API_URL}/api/generate/region/crop-and-generate/`,
            {
              world_id: world.id,
              percent_bounds: percentBounds,
              upscale: 2,
              prompt,
              provider,
            }
          );

          const image_base64 = genResp.data?.image_base64 || null;
          const crop_b64 = genResp.data?.crop_base64 || null;
          const err = genResp.data?.error || null;

          setSaveDialogMeta({
            isGenerating: false,
            provider: genResp.data?.provider || provider,
            promptUsed: genResp.data?.prompt_used || prompt,
            generationError: err,
          });

          const finalImage = image_base64 || crop_b64 || null;
          if (finalImage) {
            setCroppedRegionImage(finalImage);
            setSuggestedCoords(
              `${percentBounds.x1.toFixed(2)}%,${percentBounds.y1.toFixed(
                2
              )}% - ${percentBounds.x2.toFixed(2)}%,${percentBounds.y2.toFixed(
                2
              )}%`
            );
            // compute dimensions
            const img = new Image();
            img.onload = () =>
              setCroppedImageDimensions({
                width: img.naturalWidth,
                height: img.naturalHeight,
              });
            img.src = `data:image/png;base64,${finalImage}`;
          } else {
            setCroppedRegionImage(null);
            setCroppedImageDimensions(null);
          }
        } catch (err) {
          console.error("Crop+generate call failed", err);
          setSaveDialogMeta({
            isGenerating: false,
            provider,
            promptUsed: prompt,
            generationError: err.message || String(err),
          });
        }
      } else {
        // Simple crop
        try {
          const cropResp = await axios.post(
            `${API_URL}/api/generate/region/crop/`,
            { world_id: world.id, percent_bounds: percentBounds, upscale: 2 }
          );
          const image_base64 = cropResp.data?.image_base64 || null;
          if (image_base64) {
            setCroppedRegionImage(image_base64);
            setSuggestedCoords(
              `${percentBounds.x1.toFixed(2)}%,${percentBounds.y1.toFixed(
                2
              )}% - ${percentBounds.x2.toFixed(2)}%,${percentBounds.y2.toFixed(
                2
              )}%`
            );
            setSaveDialogMeta({
              isGenerating: false,
              provider: null,
              promptUsed: null,
              generationError: null,
            });
            setCroppedImageDimensions({
              width: cropResp.data?.width || null,
              height: cropResp.data?.height || null,
            });
            setSaveRegionDialog({ open: true });
          } else {
            alert("Crop endpoint returned no image");
          }
        } catch (err) {
          console.error("Crop failed", err);
          alert("Crop failed -- check server logs");
        }
      }
    } catch (err) {
      console.error("Region generate failed", err);
      alert("Region generation failed");
    } finally {
      setRegionDialog({ open: false, bounds: null });
    }
  };

  const handleSaveRegion = async ({ name, description }) => {
    try {
      const coordsPayload = suggestedCoords;
      await axios.post(`${API_URL}/api/generate/location/save/`, {
        name: name || `Region ${new Date().toISOString()}`,
        content: description || "",
        world_id: world.id,
        location_image: croppedRegionImage,
        image_prompt: "",
        coordinates: coordsPayload,
      });
      await loadWorld();
      await loadLocations();
    } catch (err) {
      console.error("Failed saving region", err);
      alert("Failed saving region");
    } finally {
      setSaveRegionDialog({ open: false });
      setCroppedRegionImage(null);
      setSuggestedCoords(null);
      setRegionContext(null);
    }
  };

  const handlePOIGenerate = async ({
    prompt,
    id: poiId,
    name,
    coordinates,
  }) => {
    try {
      const resp = await axios.post(
        `${API_URL}/api/generate/location/generate-image/`,
        {
          prompt,
          name,
          coordinates,
          poi_id: poiId,
        }
      );
      const { image_base64, prompt: usedPrompt } = resp.data || {};
      if (image_base64) {
        setLightboxSrc(`data:image/png;base64,${image_base64}`);
        setLightboxAlt(name || "POI Portrait");
        setLightboxOpen(true);
        const save = window.confirm("Save generated portrait for this POI?");
        if (save) {
          await axios.post(`${API_URL}/api/generate/location/save/`, {
            location_id: poiId,
            location_image: image_base64,
            image_prompt: usedPrompt,
          });
          await loadWorld();
          await loadLocations();
        }
      }
    } catch (err) {
      console.error(err);
      alert("POI generation failed.");
    } finally {
      setPoiDialog({ open: false, poi: null });
    }
  };

  const handlePOISave = async ({ imageBase64, id: poiId }) => {
    if (!imageBase64 || !poiId) return;
    try {
      await axios.post(`${API_URL}/api/generate/location/save/`, {
        location_id: poiId,
        location_image: imageBase64,
      });
      await loadWorld();
      await loadLocations();
    } catch (err) {
      console.error(err);
      alert("Failed to save POI image");
    }
  };

  const handleDelete = async () => {
    try {
      setDeleting(true);
      await axios.delete(`${API_URL}/api/worlds/${worldId}/`);
      navigate({ to: "/worlds" });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete world");
      setDeleteDialogOpen(false);
      setDeleting(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Unknown";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button component={Link} to="/worlds" startIcon={<ArrowBackIcon />}>
          Back to Worlds
        </Button>
      </Box>
    );
  }

  if (!world) {
    return (
      <Box>
        <Alert severity="warning" sx={{ mb: 3 }}>
          World not found
        </Alert>
        <Button component={Link} to="/worlds" startIcon={<ArrowBackIcon />}>
          Back to Worlds
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button
          component={Link}
          to="/worlds"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 2 }}
        >
          Back to Worlds
        </Button>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
          }}
        >
          <Box>
            <Typography variant="h3" component="h1" sx={{ fontWeight: 700 }}>
              {world.name}
            </Typography>
            <Box sx={{ display: "flex", gap: 1, mt: 2, flexWrap: "wrap" }}>
              {world.magic_system && (
                <Chip
                  label={`Magic: ${world.magic_system}`}
                  color="secondary"
                />
              )}
              {world.technology_level && (
                <Chip
                  label={`Tech: ${world.technology_level}`}
                  color="primary"
                />
              )}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Created: {formatDate(world.created_at)}
            </Typography>
            {world.updated_at && world.updated_at !== world.created_at && (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mt: 0.5 }}
              >
                Updated: {formatDate(world.updated_at)}
              </Typography>
            )}
          </Box>
          <Box sx={{ display: "flex", gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              component={Link}
              to={`/create/world?edit=${worldId}`}
            >
              Edit
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setDeleteDialogOpen(true)}
            >
              Delete
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleGenerateLandscape}
              disabled={isGenerating}
            >
              {isGenerating ? "Generating..." : "Regenerate Landscape"}
            </Button>
            <Button
              variant="outlined"
              disabled={seeding}
              onClick={async () => {
                const seedCount = 5;
                setSeeding(true);
                setSeedProgress({ done: 0, total: seedCount });
                try {
                  for (let i = 0; i < seedCount; i++) {
                    const px = Math.floor(Math.random() * 90) + 5; // 5-95
                    const py = Math.floor(Math.random() * 90) + 5;
                    // Ask the server to generate a location short description and name
                    let generatedContent = `A small place of interest.`;
                    try {
                      const genResp = await axios.post(
                        `${API_URL}/api/generate/location/`,
                        {
                          world_context:
                            world.description || world.structured_data || "",
                          location_type: "point_of_interest",
                          importance: "minor",
                          custom_details: `Seed POI at ${px}%,${py}%`,
                          provider: "groq",
                        }
                      );
                      generatedContent =
                        genResp.data?.content || generatedContent;
                    } catch (err) {
                      console.warn(
                        "POI generation call failed, using fallback content",
                        err
                      );
                    }

                    const generatedName = (
                      generatedContent.split("\n")[0] || `POI ${i + 1}`
                    ).substring(0, 120);

                    // save location
                    let saveResp = null;
                    try {
                      saveResp = await axios.post(
                        `${API_URL}/api/generate/location/save/`,
                        {
                          name: generatedName,
                          content: generatedContent,
                          world_id: world.id,
                          coordinates: `${px}%, ${py}%`,
                        }
                      );
                    } catch (err) {
                      console.error("Failed saving POI", err);
                    }

                    // Optionally generate and save portrait
                    if (autoPortraits && saveResp?.data?.id) {
                      try {
                        const locId = saveResp.data.id;
                        const imgResp = await axios.post(
                          `${API_URL}/api/generate/location/generate-image/`,
                          {
                            location_name: generatedName,
                            location_type: "point_of_interest",
                            description: generatedContent,
                          }
                        );
                        const image_base64 = imgResp.data?.image_base64;
                        const usedPrompt = imgResp.data?.prompt;
                        if (image_base64) {
                          await axios.post(
                            `${API_URL}/api/generate/location/save/`,
                            {
                              location_id: locId,
                              location_image: image_base64,
                              image_prompt: usedPrompt,
                            }
                          );
                        }
                      } catch (err) {
                        console.error("Auto portrait generation failed", err);
                      }
                    }

                    setSeedProgress((s) => ({ ...s, done: s.done + 1 }));
                  }
                } catch (err) {
                  console.error("Enhanced Seed POIs failed", err);
                  alert("Some PoI seeds failed. See console.");
                } finally {
                  setSeeding(false);
                }

                await loadWorld();
                await loadLocations();
              }}
            >
              {seeding
                ? `Seeding... (${seedProgress.done}/${seedProgress.total})`
                : "Seed POIs"}
            </Button>
            <FormControl sx={{ minWidth: 160 }} size="small">
              <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <input
                  type="checkbox"
                  checked={autoPortraits}
                  onChange={(e) => setAutoPortraits(e.target.checked)}
                />
                <span style={{ fontSize: 12 }}>Auto-generate portraits</span>
              </label>
            </FormControl>
            <FormControl sx={{ minWidth: 180 }} size="small">
              <InputLabel id="tile-provider-label">Map Style</InputLabel>
              <Select
                labelId="tile-provider-label"
                value={tileProvider}
                label="Map Style"
                onChange={(e) => setTileProvider(e.target.value)}
              >
                <MenuItem value="osm">OpenStreetMap</MenuItem>
                <MenuItem value="stamen_terrain">Stamen Terrain</MenuItem>
                <MenuItem value="stamen_watercolor">Stamen Watercolor</MenuItem>
                <MenuItem value="carto_dark">Carto Dark</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>
      </Box>
      {/* Gallery */}
      <Box
        sx={{
          display: "flex",
          gap: 2,
          my: 3,
          alignItems: "flex-start",
          flexWrap: "wrap",
        }}
      >
        {world.world_image ? (
          <Box
            sx={{ cursor: "pointer" }}
            onClick={() => {
              setLightboxSrc(`data:image/png;base64,${world.world_image}`);
              setLightboxAlt("World Landscape");
              setLightboxOpen(true);
            }}
          >
            <img
              src={`data:image/png;base64,${world.world_image}`}
              alt="landscape"
              style={{ maxHeight: 140, borderRadius: 6 }}
            />
          </Box>
        ) : (
          <Box
            sx={{
              width: 220,
              height: 140,
              bgcolor: "grey.100",
              borderRadius: 2,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexDirection: "column",
            }}
          >
            <Typography variant="body2" color="text.secondary">
              No landscape image
            </Typography>
            <Button
              size="small"
              component={Link}
              to={`/create/world?edit=${worldId}`}
            >
              Generate
            </Button>
          </Box>
        )}

        {world.world_map ? (
          <Box
            sx={{ cursor: "pointer" }}
            onClick={() => {
              setLightboxSrc(`data:image/png;base64,${world.world_map}`);
              setLightboxAlt("World Map");
              setLightboxOpen(true);
            }}
          >
            <img
              src={`data:image/png;base64,${world.world_map}`}
              alt="map"
              style={{ maxHeight: 140, borderRadius: 6 }}
            />
          </Box>
        ) : (
          <Box
            sx={{
              width: 220,
              height: 140,
              bgcolor: "grey.100",
              borderRadius: 2,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexDirection: "column",
            }}
          >
            <Typography variant="body2" color="text.secondary">
              No map image
            </Typography>
            <Button
              size="small"
              component={Link}
              to={`/create/world?edit=${worldId}`}
            >
              Generate Map
            </Button>
          </Box>
        )}
      </Box>

      {/* Map Overlay with markers if map exists */}
      {world.world_map && (
        <Box sx={{ mb: 3 }}>
          {/* If markers contain lat/lng numeric coords, show Leaflet map */}
          {(() => {
            const markerList = (
              locations.length ? locations : world.locations || []
            ).map((l) => ({
              id: l.id,
              name: l.name,
              coordinates: l.coordinates || "",
              location_image: l.location_image,
            }));

            // Try to parse first marker coordinates as lat,lng
            const latLngMarkers = markerList
              .map((m) => {
                if (!m.coordinates) return null;
                const cleaned = m.coordinates.replace(/%/g, "").trim();
                const parts = cleaned.split(/[, ]+/).filter(Boolean);
                if (parts.length !== 2) return null;
                const a = parseFloat(parts[0]);
                const b = parseFloat(parts[1]);
                if (
                  Number.isFinite(a) &&
                  Number.isFinite(b) &&
                  Math.abs(a) <= 90 &&
                  Math.abs(b) <= 180
                ) {
                  return { ...m, lat: a, lng: b };
                }
                return null;
              })
              .filter(Boolean);

            if (latLngMarkers.length > 0) {
              const provider =
                TILE_PROVIDERS[tileProvider] || TILE_PROVIDERS["osm"];
              return (
                <MapLeafletOverlay
                  markers={latLngMarkers}
                  zoom={3}
                  tileUrl={provider.url}
                  attribution={provider.attribution}
                  enableRegionDraw={true}
                  onRegionCreated={handleRegionCreated}
                  imageNaturalSize={imageNaturalSize}
                />
              );
            }

            // Otherwise render the image overlay
            return (
              <WorldImageMapOverlay
                imageBase64={world.world_map}
                markers={markerList}
                onMarkerClick={(m) => handleMarkerClick(m)}
                enableRegionDraw={true}
                onRegionCreated={handleRegionCreated}
              />
            );
          })()}
        </Box>
      )}

      <POIGenerationDialog
        open={poiDialog.open}
        poi={poiDialog.poi}
        onClose={() => setPoiDialog({ open: false, poi: null })}
        onGenerate={handlePOIGenerate}
        onSave={handlePOISave}
      />

      <RegionGenerateDialog
        open={regionDialog.open}
        regionBounds={regionDialog.bounds}
        onClose={() => setRegionDialog({ open: false, bounds: null })}
        onGenerate={handleRegionGenerate}
      />

      <SaveRegionDialog
        open={saveRegionDialog.open}
        onClose={() => setSaveRegionDialog({ open: false })}
        imageBase64={croppedRegionImage}
        suggestedName={world ? `${world.name} Region` : "Region"}
        suggestedCoords={suggestedCoords}
        onSave={handleSaveRegion}
        isGenerating={saveDialogMeta.isGenerating}
        provider={saveDialogMeta.provider}
        promptUsed={saveDialogMeta.promptUsed}
        generationError={saveDialogMeta.generationError}
        imageDimensions={croppedImageDimensions}
        onAcceptFallback={() => {
          // When user accepts fallback, keep existing croppedRegionImage (which should be crop_b64)
          setCroppedRegionImage((cur) => cur);
          // Clear generation error in meta
          setSaveDialogMeta((m) => ({ ...m, generationError: null }));
        }}
      />

      <ImageLightbox
        open={lightboxOpen}
        onClose={() => setLightboxOpen(false)}
        src={lightboxSrc}
        alt={lightboxAlt}
        caption={lightboxAlt}
      />

      {/* Content Card */}
      {world.structured_data ? (
        // Display structured world profile
        <Box>
          <Box
            sx={{
              mb: 2,
              p: 2,
              bgcolor: "primary.main",
              color: "white",
              borderRadius: 1,
              display: "flex",
              alignItems: "center",
              gap: 1,
            }}
          >
            <Chip
              label="Structured Profile"
              size="small"
              sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }}
            />
            <Typography variant="body2">
              This world uses the new structured format with organized sections
            </Typography>
          </Box>
          <StructuredWorldDisplay worldProfile={world.structured_data} />
        </Box>
      ) : (
        // Display legacy world format
        <Card>
          <CardContent>
            {/* Description */}
            {world.description && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Description
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                  {world.description}
                </Typography>
              </Box>
            )}

            {world.description && world.history && <Divider sx={{ my: 3 }} />}

            {/* History */}
            {world.history && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  History
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                  {world.history}
                </Typography>
              </Box>
            )}

            {world.history && world.geography && <Divider sx={{ my: 3 }} />}

            {/* Geography */}
            {world.geography && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Geography
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                  {world.geography}
                </Typography>
              </Box>
            )}

            {world.geography && world.culture && <Divider sx={{ my: 3 }} />}

            {/* Culture */}
            {world.culture && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Culture
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                  {world.culture}
                </Typography>
              </Box>
            )}

            {world.culture && world.lore && <Divider sx={{ my: 3 }} />}

            {/* Lore */}
            {world.lore && (
              <Box>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Lore
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                  {world.lore}
                </Typography>
              </Box>
            )}

            {!world.description &&
              !world.history &&
              !world.geography &&
              !world.culture &&
              !world.lore && (
                <Typography variant="body2" color="text.secondary">
                  No content available for this world yet.
                </Typography>
              )}
          </CardContent>
        </Card>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => !deleting && setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete World?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete <strong>{world.name}</strong>? This
            action cannot be undone and will also delete all associated
            locations.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setDeleteDialogOpen(false)}
            disabled={deleting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDelete}
            color="error"
            variant="contained"
            disabled={deleting}
          >
            {deleting ? "Deleting..." : "Delete"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
