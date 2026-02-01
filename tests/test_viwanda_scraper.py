import json
from pathlib import Path
import pytest

import app.services.viwanda_scraper as scraper


class MockResponse:
    def __init__(self, text=None, content=None, status_code=200):
        self.text = text or ""
        self.content = content or b""
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("HTTP error")

    def iter_content(self, chunk_size=8192):
        yield self.content


def test_fetch_document_links_and_download(monkeypatch, tmp_path):
    # Mock page HTML that includes two file links (one relative, one absolute)
    # Two-page scenario: page1 links test1.pdf and next->page2; page2 links test1.pdf (duplicate) and test2.xlsx
    html_page1 = '''
    <html>
      <body>
        <a href="/documents/files/test1.pdf">file1</a>
        <a href="/documents/product-prices-domestic?page=2">next</a>
      </body>
    </html>
    '''
    html_page2 = '''
    <html>
      <body>
        <a href="/documents/files/test1.pdf">file1</a>
        <a href="https://www.viwanda.go.tz/docs/other/test2.xlsx">file2</a>
      </body>
    </html>
    '''

    def fake_get(url, *args, **kwargs):
        if url.endswith("product-prices-domestic") and "page=2" not in url:
            return MockResponse(text=html_page1)
        elif "page=2" in url:
            return MockResponse(text=html_page2)
        elif url.endswith("test1.pdf"):
            return MockResponse(content=b"PDFDATA1")
        elif url.endswith("test2.xlsx"):
            return MockResponse(content=b"XLSXDATA2")
        else:
            return MockResponse(status_code=404)

    monkeypatch.setattr(scraper, "requests", type("R", (), {"get": staticmethod(fake_get)}))

    saved = scraper.scrape_viwanda_save(page_url="https://www.viwanda.go.tz/documents/product-prices-domestic", save_dir=str(tmp_path / "viwanda"))

    # Should only download the two unique files once each
    assert len(saved) == 2
    p1 = Path(saved[0])
    p2 = Path(saved[1])
    assert p1.exists() and p2.exists()

    contents = {p1.read_bytes(), p2.read_bytes()}
    assert contents == {b"PDFDATA1", b"XLSXDATA2"}


def test_fetch_document_links_ignores_empty_and_js_hrefs(monkeypatch):
    html = '''
    <html>
      <body>
        <a href="">empty</a>
        <a href="#">hash</a>
        <a href="javascript:void(0)">js</a>
        <a href="/documents/files/test.pdf">file</a>
      </body>
    </html>
    '''

    def fake_get(url, *args, **kwargs):
        return MockResponse(text=html)

    monkeypatch.setattr(scraper, "requests", type("R", (), {"get": staticmethod(fake_get)}))

    links = scraper.fetch_document_links("https://www.viwanda.go.tz/documents/product-prices-domestic")
    assert links == ["https://www.viwanda.go.tz/documents/files/test.pdf"]


def test_fetch_document_links_next_handles_none_class(monkeypatch):
    html = '''
    <html>
      <body>
        <a href="/documents/files/test1.pdf">file1</a>
        <a>no class anchor</a>
        <a href="/documents/product-prices-domestic?page=2" class="page next">Next</a>
      </body>
    </html>
    '''

    def fake_get(url, *args, **kwargs):
        return MockResponse(text=html)

    monkeypatch.setattr(scraper, "requests", type("R", (), {"get": staticmethod(fake_get)}))

    links, next_url = scraper.fetch_document_links_and_next("https://www.viwanda.go.tz/documents/product-prices-domestic")
    assert links == ["https://www.viwanda.go.tz/documents/files/test1.pdf"]
    assert next_url is not None and "page=2" in next_url
