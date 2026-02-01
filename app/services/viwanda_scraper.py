import os
import logging
import hashlib
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# File extensions to consider
FILE_EXTENSIONS = {".pdf", ".xls", ".xlsx", ".csv", ".zip", ".doc", ".docx", ".txt"}

DEFAULT_PAGE = "https://www.viwanda.go.tz/documents/product-prices-domestic"


def _is_file_link(href: str) -> bool:
    if not href:
        return False
    try:
        parsed = urlparse(href)
        path = (parsed.path or "").lower()
        return any(path.endswith(ext) for ext in FILE_EXTENSIONS)
    except Exception:
        return False


def _safe_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    # fallback
    if not name:
        name = url.replace("/", "_")
    return name


def _hash_file(path: Path, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_document_links_and_next(page_url: str = DEFAULT_PAGE) -> (List[str], Optional[str]):
    """Fetch file links and optional next-page link from a page."""
    logger.info(f"Fetching document list from {page_url}")
    resp = requests.get(page_url, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        if _is_file_link(href):
            full = urljoin(page_url, href)
            links.append(full)

    # Try to find a "next" page link
    next_url = None
    # look for rel=next links
    next_link = soup.find("link", rel="next") or soup.find("a", rel="next")
    if not next_link:
        # look for anchor text "next" or classes containing "next"
        next_link = soup.find("a", string=lambda t: t and "next" in t.lower())
        if not next_link:
            # Fixed: properly handle None values for class attribute and make case-insensitive
            def has_next_class(c):
                if c is None:
                    return False
                if isinstance(c, (list, tuple)):
                    return "next" in " ".join(c).lower()
                return "next" in c.lower()

            next_link = soup.find("a", class_=has_next_class)

    if next_link and next_link.get("href"):
        next_url = urljoin(page_url, next_link.get("href"))

    logger.info(f"Found {len(links)} file links, next page: {next_url}")
    return links, next_url


def _download_and_dedupe(url: str, save_dir: Path, existing_hashes: dict) -> Optional[Path]:
    """Download to a temp file, hash it, and skip saving if duplicate by content. Returns Path to saved file or existing file if duplicate."""
    save_dir.mkdir(parents=True, exist_ok=True)
    # Create temporary file with delete=False so we can manage it ourselves
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp_path = Path(tmp.name)
    tmp.close()  # Close the file handle immediately after getting the name

    try:
        logger.info(f"Downloading {url} to temp {tmp_path}")
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        h = hashlib.sha256()

        # Write to the temp file
        with open(tmp_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    h.update(chunk)
        # File is now closed after the with block

        file_hash = h.hexdigest()

        # If hash exists, don't save duplicate
        if file_hash in existing_hashes:
            logger.info(f"Duplicate file detected by content hash, skipping save: {url}")
            tmp_path.unlink(missing_ok=True)
            return Path(existing_hashes[file_hash])

        # Determine filename and move temp file to target
        filename = _safe_filename_from_url(url)
        target = save_dir / filename
        if target.exists():
            base = target.stem
            ext = target.suffix
            i = 1
            while True:
                candidate = save_dir / f"{base}_{i}{ext}"
                if not candidate.exists():
                    target = candidate
                    break
                i += 1

        # Move the file - should work now that all handles are closed
        shutil.move(str(tmp_path), str(target))
        existing_hashes[file_hash] = str(target)
        return target

    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise


def scrape_viwanda_save(page_url: str = DEFAULT_PAGE, save_dir: str = "uploads/viwanda", follow_pagination: bool = True, max_pages: int = 50) -> List[str]:
    """Scrape the Viwanda documents page and download all found files.

    - Follows pagination when `follow_pagination` is True by trying to find "next" links.
    - Avoids duplicate downloads by URL and by file content hash.

    Returns a list of saved file paths (as strings).
    """
    save_path = Path(save_dir)
    saved = []
    try:
        to_visit = [page_url]
        visited_pages: Set[str] = set()
        file_urls: Set[str] = set()

        pages_crawled = 0
        while to_visit and pages_crawled < max_pages:
            url = to_visit.pop(0)
            if url in visited_pages:
                continue
            visited_pages.add(url)
            pages_crawled += 1

            try:
                links, next_url = fetch_document_links_and_next(url)
                for l in links:
                    file_urls.add(l)
                if follow_pagination and next_url and next_url not in visited_pages:
                    to_visit.append(next_url)
            except Exception as e:
                logger.error(f"Failed to fetch page {url}: {e}")

        # Download unique file URLs and avoid duplicates by content hash
        existing_hashes = {}
        # preload existing files' hashes
        if save_path.exists():
            for f in save_path.iterdir():
                if f.is_file():
                    try:
                        h = _hash_file(f)
                        existing_hashes[h] = str(f)
                    except Exception:
                        continue

        for link in sorted(file_urls):
            try:
                p = _download_and_dedupe(link, save_path, existing_hashes)
                if p:
                    saved.append(str(p))
            except Exception as e:
                logger.error(f"Failed to download {link}: {e}")
    except Exception as e:
        logger.error(f"Error scraping viwanda page: {e}")
        raise

    logger.info(f"Downloaded {len(saved)} files to {save_path}")
    return saved
