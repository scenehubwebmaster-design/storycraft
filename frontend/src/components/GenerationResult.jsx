import { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Tabs,
  Tab,
} from "@mui/material";
import ReactMarkdown from "react-markdown";
import EditIcon from "@mui/icons-material/Edit";
import SaveIcon from "@mui/icons-material/Save";
import RefreshIcon from "@mui/icons-material/Refresh";

/**
 * GenerationResult - Display and manage AI-generated content
 */
export default function GenerationResult({
  content,
  onSave,
  onRefine,
  saving = false,
  entity = "content",
  isEditMode = false,
}) {
  const [activeTab, setActiveTab] = useState(0);
  const [editedContent, setEditedContent] = useState(content);
  const [refinementInstructions, setRefinementInstructions] = useState("");

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSave = () => {
    onSave(editedContent);
  };

  const handleRefine = () => {
    onRefine(refinementInstructions);
    setRefinementInstructions("");
  };

  if (!content) {
    return (
      <Paper sx={{ p: 3, textAlign: "center" }}>
        <Typography color="text.secondary">
          Generate {entity} to see results here
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Preview" />
          <Tab label="Edit" />
          <Tab label="Refine" />
        </Tabs>
      </Box>

      {/* Preview Tab */}
      {activeTab === 0 && (
        <Box sx={{ minHeight: 400, maxHeight: 600, overflowY: "auto", p: 2 }}>
          <ReactMarkdown>{content}</ReactMarkdown>
        </Box>
      )}

      {/* Edit Tab */}
      {activeTab === 1 && (
        <Box>
          <textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            style={{
              width: "100%",
              minHeight: 400,
              padding: "16px",
              fontFamily: "monospace",
              fontSize: "14px",
              border: "1px solid #444",
              borderRadius: "4px",
              backgroundColor: "#1e1e1e",
              color: "#fff",
            }}
          />
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
            disabled={saving}
            sx={{ mt: 2 }}
          >
            {saving ? (
              <CircularProgress size={20} />
            ) : isEditMode ? (
              "Update Changes"
            ) : (
              "Save Changes"
            )}
          </Button>
        </Box>
      )}

      {/* Refine Tab */}
      {activeTab === 2 && (
        <Box>
          <Alert severity="info" sx={{ mb: 2 }}>
            Describe how you'd like to refine this {entity}. The AI will iterate
            on the existing content based on your instructions.
          </Alert>
          <textarea
            value={refinementInstructions}
            onChange={(e) => setRefinementInstructions(e.target.value)}
            placeholder={`E.g., "Make the character more mysterious" or "Add more vivid descriptions"`}
            style={{
              width: "100%",
              minHeight: 200,
              padding: "16px",
              fontFamily: "monospace",
              fontSize: "14px",
              border: "1px solid #444",
              borderRadius: "4px",
              backgroundColor: "#1e1e1e",
              color: "#fff",
            }}
          />
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={handleRefine}
            disabled={!refinementInstructions.trim() || saving}
            sx={{ mt: 2 }}
          >
            Refine with AI
          </Button>
        </Box>
      )}

      <Divider sx={{ my: 3 }} />

      <Box sx={{ display: "flex", gap: 2 }}>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSave}
          disabled={saving}
          fullWidth
        >
          {saving ? (
            <CircularProgress size={20} />
          ) : isEditMode ? (
            `Update ${entity}`
          ) : (
            `Save ${entity}`
          )}
        </Button>
      </Box>
    </Paper>
  );
}
