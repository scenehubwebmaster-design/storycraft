Read PDF MCP test

This folder contains `read_pdf_test.js` which launches the `@sylphlab/pdf-reader-mcp`
server via `npx` and sends a single `read_pdf` request for page 2 of a local PDF
at `./documents/PlayersHandbook2024.pdf`.

How to run

1. Place the PDF file at `e:\storycraft\documents\PlayersHandbook2024.pdf` (or adjust the
   path in `scripts/read_pdf_test.js`).
2. From the repo root run:

```powershell
npm run test:read-pdf
```

Notes

- The script spawns `npx @sylphlab/pdf-reader-mcp` and pipes a JSON request to
  stdin. The MCP server must be reachable via npx (i.e. network and npm config
  working). If the MCP server requires local build or Docker, follow the
  project's README instead.
- If the MCP server restricts local file access to the project root, ensure the
  PDF is placed under the repo (as above).
