# Mistral-OCR Repository Guide

## Project Overview

- Repository for working with Mistral AI's OCR and document understanding capabilities
- Contains PDF documents for processing and analysis
- Documentation of various cybersecurity standards and frameworks

## CLI Tool Usage

```bash
# Install requirements
python3 -m pip install -r requirements.txt

# Run the CLI tool (API key from environment variable)
MISTRAL_API_KEY=your_api_key python3 mistral_ocr_cli.py

# Dry run (show what would be processed without actually processing)
MISTRAL_API_KEY=your_api_key python3 mistral_ocr_cli.py --dry-run

# Process specific files
MISTRAL_API_KEY=your_api_key python3 mistral_ocr_cli.py --files "document/*.pdf"

# Force reprocessing of existing files
MISTRAL_API_KEY=your_api_key python3 mistral_ocr_cli.py --force

# Adjust retry attempts for API errors
MISTRAL_API_KEY=your_api_key python3 mistral_ocr_cli.py --max-retries 5

# Control delay between files to avoid rate limits
MISTRAL_API_KEY=your_api_key python3 mistral_ocr_cli.py --delay 5.0
```

## Development Commands

- No build/test/lint commands as this is primarily a documentation repository
- Uses Mistral AI Python client for OCR processing

## OCR Usage in Custom Scripts

```python
# Process a PDF document with OCR
from mistralai import Mistral
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={"type": "document_url", "document_url": "your_document_url"}
)
```

## Document Structure

- `/pdf/` - Contains PDF documents organized by category/standard
- `/markdown/` - Directory for storing OCR-extracted markdown content
- `mistral_ocr_cli.py` - CLI tool for batch processing PDFs to markdown

## Workflow Suggestions

- Use the CLI tool for batch processing all PDFs
- For individual documents, use direct API calls
- Store OCR results as markdown files in the `/markdown/` directory
