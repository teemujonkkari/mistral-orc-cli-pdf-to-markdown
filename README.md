# Mistral OCR CLI Tool

> 🤖 This project was created with [Claude Code](https://claude.ai/code)

A command-line tool for batch processing PDF documents using the Mistral AI OCR API.

## Overview

This tool automatically scans your PDF documents, processes them using Mistral's advanced OCR capabilities, and saves the results as markdown files. It preserves your folder structure and avoids reprocessing documents that have already been converted.

## Features

- Recursive scanning of PDF documents in folder hierarchies
- Automatic markdown conversion using Mistral's OCR API
- Preservation of folder structure between PDF and markdown files
- Skip processing for documents that are already converted
- Progress logging and error handling
- Dry-run mode to preview operations

## Requirements

- Python 3.6+
- `mistralai` Python package
- Mistral AI API key

## Installation

1. Clone this repository:

```bash
git clone https://github.com/teemujonkkari/mistral-orc-cli-pdf-to-markdown.git
cd mistral-orc-cli-pdf-to-markdown
```

2. Install required dependencies:

```bash
python3 -m pip install -r requirements.txt
```

If pip isn't found, you may need to ensure it's installed:

```bash
python3 -m ensurepip --upgrade
```

## Usage

Run the tool with your Mistral API key as an environment variable:

```bash
MISTRAL_API_KEY=your_api_key python3 mistral_ocr_cli.py
```

### Options

- `--dry-run`: Show what would be processed without making any API calls or creating files
- `--files FILE1 FILE2 ...`: Process specific files instead of all PDFs (can use patterns like "\*.pdf")
- `--force`: Process files even if markdown already exists
- `--max-retries N`: Maximum number of retry attempts for API errors (default: 3)
- `--delay SECONDS`: Delay in seconds between processing files to avoid rate limits (default: 3.0)

## Directory Structure

- `/pdf/`: Place your PDF documents here (with any subfolder structure)
- `/markdown/`: Converted markdown files will be saved here (matching the PDF structure)

## Example

If your PDF files are organized like this:

```
pdf/
├── document1.pdf
└── standards/
    └── nis2.pdf
```

After running the tool, your markdown files will be organized like this:

```
markdown/
├── document1.md
└── standards/
    └── nis2.md
```

## License

MIT

## Credits

This tool uses the Mistral AI OCR API for document processing.
