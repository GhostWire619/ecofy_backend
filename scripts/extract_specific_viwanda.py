"""Script to extract a specific Viwanda document to CSV using Gemini document service."""
import sys
import os
# Ensure project root is on sys.path so `app` imports work when running script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from app.services.document_gemini_service import document_service

# Specific file to extract
input_file = "uploads/viwanda/sw-1623060287-Wholesale prices Report  04th June, 2021 (1).pdf"
output_dir = Path("uploads/viwanda_csv")
output_dir.mkdir(parents=True, exist_ok=True)

input_path = Path(input_file)
if not input_path.exists():
    print(f"Input file not found: {input_file}")
    raise SystemExit(1)

output_path = output_dir / (input_path.stem + ".csv")

print(f"Extracting from: {input_path}")
print("Sending document to Gemini for CSV extraction...")

# Custom prompt for tabular data
prompt = (
    "Extract the wholesale price data from this document. "
    "The document contains a table with crop/commodity prices across different regions. "
    "Return ONLY CSV content with headers. "
    "Include columns for: Region, Commodity, Min Price, Max Price, etc. "
    "Do not include any explanation or markdown, return raw CSV."
)

try:
    # Extract text from PDF using pypdf
    from pypdf import PdfReader
    reader = PdfReader(str(input_path))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    print(f"Extracted text length: {len(text)}")
    print("First 500 chars of text:")
    print(repr(text[:500]))
    
    # Now send the text to Gemini for CSV conversion
    text_prompt = (
        "Convert the following wholesale price data into CSV format. "
        "The data contains crop/commodity prices across different regions. "
        "Return ONLY CSV content with headers. "
        "Include columns for: Region, Commodity, Min Price, Max Price, etc. "
        "Do not include any explanation or markdown, return raw CSV."
    )
    
    result = document_service.extract_from_document(
        file_bytes=text.encode('utf-8'),
        mime_type="text/plain",
        prompt=text_prompt,
        return_json=False,
        response_mime_type="text/plain"
    )
    
    print("Gemini CSV response:")
    print(result[:1000])
    
    # Save the result
    output_path.write_text(result, encoding="utf-8")
    print(f"Saved CSV to: {output_path}")
    
except Exception as e:
    print(f"Extraction failed: {type(e).__name__} {e}")
    raise SystemExit(1)