#!/usr/bin/env python3

import os
import sys
import argparse
from pathlib import Path
import time
from mistralai import Mistral
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_api_key():
    """Get Mistral API key from environment variable"""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        logger.error("MISTRAL_API_KEY environment variable not set")
        sys.exit(1)
    return api_key

def get_markdown_filename(pdf_path):
    """Generate corresponding markdown filename for a PDF"""
    relative_path = pdf_path.relative_to(Path('pdf'))
    markdown_path = Path('markdown').joinpath(relative_path)
    
    # Create parent directory if it doesn't exist
    markdown_parent = markdown_path.parent
    if not markdown_parent.exists():
        markdown_parent.mkdir(parents=True, exist_ok=True)
    
    # Change extension to .md
    return markdown_path.with_suffix('.md')

def process_pdf(client, pdf_path, markdown_path, max_retries=3):
    """Process PDF with Mistral OCR and save as markdown"""
    logger.info(f"Processing {pdf_path}")
    
    # Retry loop for handling temporary server errors
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Upload the PDF file
            try:
                with open(pdf_path, "rb") as f:
                    file_content = f.read()
                
                uploaded_pdf = client.files.upload(
                    file={
                        "file_name": pdf_path.name,
                        "content": file_content,
                    },
                    purpose="ocr"
                )
            except Exception as e:
                error_message = str(e)
                if "401" in error_message:
                    logger.error("Authentication failed. Check your API key is correct and valid.")
                    logger.error("Make sure to set the MISTRAL_API_KEY environment variable with a valid key.")
                    return False
                elif "502" in error_message or "Bad Gateway" in error_message:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = 5 * retry_count  # Progressive backoff: 5s, 10s, 15s
                        logger.warning(f"Mistral API temporary error (502). Retrying in {wait_time}s... (Attempt {retry_count}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Mistral API unavailable after {max_retries} attempts. Please try again later.")
                        return False
                else:
                    raise e
            
            # Get signed URL for the uploaded file
            signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
            
            # Process with OCR
            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": signed_url.url,
                }
            )
            
            # Combine all pages into one markdown file
            markdown_content = ""
            for page in ocr_response.pages:
                markdown_content += f"## Page {page.index}\n\n"
                markdown_content += page.markdown + "\n\n"
            
            # Save to markdown file
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Saved markdown to {markdown_path}")
            
            # Add a small delay to avoid hitting rate limits
            time.sleep(2)
            
            return True
            
        except Exception as e:
            error_message = str(e)
            if "401" in error_message:
                logger.error("Authentication failed. Check your API key is correct and valid.")
                logger.error("Make sure to set the MISTRAL_API_KEY environment variable with a valid key.")
                return False
            elif "502" in error_message or "Bad Gateway" in error_message or "timeout" in error_message.lower():
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 5 * retry_count  # Progressive backoff: 5s, 10s, 15s
                    logger.warning(f"Mistral API temporary error. Retrying in {wait_time}s... (Attempt {retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Mistral API unavailable after {max_retries} attempts. Please try again later.")
                    return False
            else:
                logger.error(f"Error processing {pdf_path}: {error_message}")
                return False
    
    # If we get here, we exhausted all retries
    return False

def check_api_connection(client):
    """Check if we can connect to the Mistral API with the provided key"""
    try:
        # Make a simple API call to test connection and authentication
        # Just getting models is a lightweight operation
        client.models.list()
        return True
    except Exception as e:
        error_message = str(e)
        if "401" in error_message:
            logger.error("API key authentication failed. Please check your MISTRAL_API_KEY.")
            logger.error("You can get an API key from https://console.mistral.ai/")
        elif "502" in error_message or "Bad Gateway" in error_message:
            logger.error("Mistral API service is temporarily unavailable (502 Bad Gateway).")
            logger.error("Please wait a few minutes and try again.")
        else:
            logger.error(f"API connection error: {error_message}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Convert PDFs to markdown using Mistral OCR")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be processed without actually processing")
    parser.add_argument("--files", nargs="+", help="Specific PDF files to process (relative to the pdf/ directory)")
    parser.add_argument("--force", action="store_true", help="Process files even if markdown already exists")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum number of retries for API errors")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay in seconds between processing files (default: 3.0)")
    args = parser.parse_args()
    
    # Get API key and initialize client
    api_key = get_api_key()
    client = Mistral(api_key=api_key)
    
    # Check API connection if not in dry-run mode
    if not args.dry_run:
        logger.info("Testing API connection...")
        if not check_api_connection(client):
            logger.error("API connection failed. Exiting.")
            sys.exit(1)
        logger.info("API connection successful!")
    
    # Create markdown directory if it doesn't exist
    markdown_dir = Path('markdown')
    if not markdown_dir.exists():
        markdown_dir.mkdir(parents=True, exist_ok=True)
    
    # Find PDF files
    pdf_dir = Path('pdf')
    
    if args.files:
        # Process specific files
        pdf_files = []
        for file_pattern in args.files:
            # Handle both absolute paths and paths relative to pdf/
            if Path(file_pattern).is_absolute():
                if Path(file_pattern).exists():
                    pdf_files.append(Path(file_pattern))
                else:
                    logger.warning(f"File not found: {file_pattern}")
            else:
                # Treat as relative to pdf/
                relative_path = pdf_dir / file_pattern
                if relative_path.exists():
                    pdf_files.append(relative_path)
                else:
                    # Try with wildcards
                    matching_files = list(pdf_dir.glob(file_pattern))
                    if matching_files:
                        pdf_files.extend(matching_files)
                    else:
                        logger.warning(f"No files found matching: {file_pattern}")
    else:
        # Find all PDFs recursively
        pdf_files = list(pdf_dir.glob('**/*.pdf'))
    
    if not pdf_files:
        logger.info("No PDF files found to process")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    # Process each PDF
    processed_count = 0
    skipped_count = 0
    failed_count = 0
    
    for i, pdf_path in enumerate(pdf_files):
        markdown_path = get_markdown_filename(pdf_path)
        
        # Skip if markdown file already exists and not forcing
        if markdown_path.exists() and not args.force:
            logger.info(f"Skipping {pdf_path} (already processed)")
            skipped_count += 1
            continue
        
        if args.dry_run:
            logger.info(f"Would process: {pdf_path} -> {markdown_path}")
            processed_count += 1
            continue
        
        # Add delay between files (but not before the first one)
        if i > 0:
            logger.info(f"Waiting {args.delay} seconds before processing next file...")
            time.sleep(args.delay)
        
        success = process_pdf(client, pdf_path, markdown_path, max_retries=args.max_retries)
        if success:
            processed_count += 1
        else:
            failed_count += 1
    
    logger.info(f"Processing complete. Processed: {processed_count}, Skipped: {skipped_count}, Failed: {failed_count}")

if __name__ == "__main__":
    main()