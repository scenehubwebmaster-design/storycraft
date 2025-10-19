import React from "react";
import { Dialog, DialogContent, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

export default function ImageLightbox({ open, onClose, src, alt, caption }) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg">
      <IconButton
        aria-label="close"
        onClick={onClose}
        sx={{ position: "absolute", right: 8, top: 8, zIndex: 10 }}
      >
        <CloseIcon />
      </IconButton>
      <DialogContent
        sx={{ p: 0, backgroundColor: "black", textAlign: "center" }}
      >
        <img
          src={src}
          alt={alt}
          onClick={onClose}
          style={{
            display: "block",
            maxWidth: "90vw",
            maxHeight: "85vh",
            margin: "0 auto",
            cursor: "zoom-out",
          }}
        />
        {caption && (
          <div style={{ color: "#fff", opacity: 0.9, padding: "8px 12px" }}>
            {caption}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
