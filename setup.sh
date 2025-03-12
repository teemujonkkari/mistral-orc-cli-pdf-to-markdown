#!/bin/bash

# Ensure pip is available
echo "Ensuring pip is installed..."
python3 -m ensurepip --upgrade

# Install required packages
echo "Installing required packages..."
python3 -m pip install -r requirements.txt

# Make script executable
echo "Making OCR script executable..."
chmod +x mistral_ocr_cli.py

echo ""
echo "Setup complete! You can now run the OCR tool with:"
echo "MISTRAL_API_KEY=your_api_key ./mistral_ocr_cli.py"
echo ""
echo "For a dry run (to see what would be processed without actually processing):"
echo "MISTRAL_API_KEY=your_api_key ./mistral_ocr_cli.py --dry-run"