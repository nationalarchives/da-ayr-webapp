"""
Benchmark for app.main.util.render_utils.search_within_pdf.

Builds one large plain-text PDF in memory (no S3, no running server, no
auth), then times a separate search_within_pdf() call per term against
that same document, each term matching a different number of times - so
search time scales with match count, not with the document changing
between runs.

Usage:
    poetry run python performance_tests/search_within_pdf_bench.py
"""

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pymupdf
from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main.util.render_utils import search_within_pdf  # noqa: E402

FILLER_TEXT = "The quick brown fox jumps over the lazy dog. " * 40

PAGES = 3000
TERMS = {
    "raretermxyz": 1,
    "uncommontermxyz": 25,
    "commontermxyz": 1000,
    "frequenttermxyz": 8000,
}


def build_single_large_pdf(pages: int, terms: dict) -> bytes:
    """Build one large, plain-text PDF (no images) where each term in
    `terms` appears the given number of times, spread evenly across the
    document. Deliberately minimal - just enough per-page content for
    search_for to do real work at a realistic page count.
    """
    doc = pymupdf.open()
    for _ in range(pages):
        doc.new_page()

    for page_num in range(pages):
        doc.load_page(page_num).insert_text((50, 50), FILLER_TEXT[:200])

    for term, count in terms.items():
        for i in range(count):
            page_num = i % pages
            y = 80 + 12 * (i // pages)
            doc.load_page(page_num).insert_text((50, y), term)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def time_search(pdf_bytes: bytes, term: str) -> tuple[int, float]:
    """Run search_within_pdf for one term against pdf_bytes, returning
    (hit count, elapsed seconds)."""
    app = Flask(__name__)
    with patch(
        "app.main.util.render_utils.get_pdf_from_s3", return_value=pdf_bytes
    ):
        with app.app_context():
            t0 = time.perf_counter()
            response = search_within_pdf(
                query=term, bucket="bench", key="bench"
            )
            elapsed = time.perf_counter() - t0
    return response.get_json()["total"], elapsed


def format_kb(kb: float) -> str:
    return f"{kb / 1024:.1f} MB" if kb >= 1024 else f"{kb:.0f} KB"


def main() -> None:
    t0 = time.perf_counter()
    pdf_bytes = build_single_large_pdf(PAGES, TERMS)
    build_s = time.perf_counter() - t0
    pdf_kb = len(pdf_bytes) / 1024

    print(
        f"One document: {PAGES} pages, {format_kb(pdf_kb)}, "
        f"built once in {build_s:.1f}s\n"
    )
    header = f"{'term':>18}  {'hits':>7}  {'search':>9}"
    print(header)
    print("-" * len(header))
    for term in TERMS:
        hits, search_s = time_search(pdf_bytes, term)
        print(f"{term:>18}  {hits:>7}  {search_s:>8.3f}s")


if __name__ == "__main__":
    main()
