"""Script to extract a Viwanda document to CSV using Gemini document service."""
import sys
import os
# Ensure project root is on sys.path so `app` imports work when running script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from pathlib import Path
from app.services.document_gemini_service import document_service

# Choose a sample file from uploads/viwanda (only files with 'prices' in the name)
viwanda_dir = Path("uploads/viwanda")
if not viwanda_dir.exists():
    print("No uploads/viwanda directory found. Run scraper first.")
    raise SystemExit(1)

# Filter for files that contain 'prices' in the filename (case-insensitive)
candidates = [p for p in viwanda_dir.iterdir() if p.is_file() and "prices" in p.name.lower()]
if not candidates:
    print("No files with 'prices' in the filename found in uploads/viwanda")
    raise SystemExit(1)

# Sort by modified time (most recent first)
files_sorted = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)

# Validate each candidate: prefer PDFs with at least 1 page
valid_candidates = []
for p in files_sorted:
    print(f"Checking candidate: {p}")
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(p))
        pages = len(reader.pages)
        print(f" - pages: {pages}")
        if pages > 0:
            valid_candidates.append(p)
        else:
            print(" - skipped (no pages)")
    except Exception as e:
        # If pypdf is not available or cannot read, warn and skip
        print(f" - pypdf error or unreadable file: {type(e).__name__} {e}")
        print(" - skipping to next candidate")

if not valid_candidates:
    print("No valid 'prices' files with pages found.")
    raise SystemExit(1)

out_dir = Path("uploads/viwanda_csv")
out_dir.mkdir(parents=True, exist_ok=True)

# Try extraction for each valid candidate until one succeeds
for p in valid_candidates:
    print(f"Attempting extraction for: {p}")
    output_path = out_dir / (p.stem + ".csv")
    print("Sending document to Gemini for CSV extraction...")
    try:
        csv_path = document_service.extract_document_to_csv(str(p), str(output_path))
        print(f"Saved CSV to: {csv_path}")
        break
    except Exception as e:
        print(f"Extraction failed for {p.name}: {type(e).__name__} {e}")
        print(" - moving to next candidate")
else:
    print("All extraction attempts failed.")
    raise SystemExit(1)
