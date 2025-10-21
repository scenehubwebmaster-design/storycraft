# PDF extraction helpers

This folder contains `extract_phb.py`, a simple extractor that uses `pdfplumber` and falls back to OCR via `pytesseract` + `pdf2image`.

Windows prerequisites (for OCR fallback)

- Tesseract:

  - Install from https://github.com/tesseract-ocr/tesseract or via Chocolatey:
    ```powershell
    choco install tesseract
    ```
  - Ensure the Tesseract binary directory (e.g. `C:\Program Files\Tesseract-OCR`) is in your PATH.

- Poppler (for pdf2image):
  - Download prebuilt binaries from https://github.com/oschwartz10612/poppler-windows/releases .
  - Unzip and add the `bin` directory to your PATH, or pass `--poppler-path "C:\path\to\poppler\Library\bin"` to the script.

Usage example:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ..\requirements.txt
.\.venv\Scripts\python.exe .\scripts\extract_phb.py --pdf .\documents\PlayersHandbook2024.pdf --pages 1-5 --out .\data\phb\raw_pages.json --poppler-path "C:\tools\poppler-23.05.0\Library\bin"
```

If `--poppler-path` is not provided, the script will attempt to call `pdf2image` with system PATH.
