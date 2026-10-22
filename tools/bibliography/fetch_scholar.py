#!/usr/bin/env python3
"""
Fetch publications from Semantic Scholar for a list of authors,
deduplicate, and export a merged .bib file with fields needed by al-folio:
  - doi
  - altmetric = {true}
  - dimensions = {true}

Note: does NOT set google_scholar_id. Al-folio's Scholar badge needs a
per-paper Scholar citation code (from the URL when you click a paper on
a Scholar profile), which Semantic Scholar has no equivalent for. Writing
an author's own Scholar profile ID into that field produces a broken badge
that 404s at build time -- don't reintroduce it.

Uses the free Semantic Scholar API (no key required, no scraping, no captchas).

Usage (from the repository root):
    python3 tools/bibliography/fetch_scholar.py              # fetch all papers
    python3 tools/bibliography/fetch_scholar.py --refresh    # start with an empty cache
    python3 tools/bibliography/fetch_scholar.py --limit 10   # test: 10 most recent pubs per author

Cache:
    scholar_cache.json  — stores raw S2 paper dicts keyed by paperId.
    Bookkeeping only; every run re-fetches all papers. Not committed.

Output:
    merged_papers.bib  — scratch file, overwritten every run. Not committed.
    Merge it into _bibliography/papers.bib with merge_bibliography.py.

Both files are written next to this script by default (see --out and --cache).
"""

import time
import re
import sys
import json
import os
import argparse
import httpx

# ── Configuration ─────────────────────────────────────────────────────────────

# Semantic Scholar author IDs
# Find at: https://api.semanticscholar.org/graph/v1/author/search?query=<name>
AUTHORS = [
    {"name": "Dave Wolk",        "s2_id": "2256503361"},
    {"name": "Sandy Das",        "s2_id": "2202284615"},
    {"name": "Paul Yushkevich",  "s2_id": "144809529"},
]

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "merged_papers.bib")
CACHE_FILE  = os.path.join(SCRIPT_DIR, "scholar_cache.json")

# Delay between paginated requests (S2 allows ~1 req/s without an API key)
DELAY = 1.1

S2_BASE = "https://api.semanticscholar.org/graph/v1"

PAPER_FIELDS = (
    "title,authors,year,venue,journal,externalIds,"
    "publicationTypes,publicationDate,abstract,"
    "citationCount,openAccessPdf"
)

# ── Cache ─────────────────────────────────────────────────────────────────────

def load_cache(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print(f"  Cache saved ({len(cache)} entries) -> {path}")

# ── S2 API helpers ────────────────────────────────────────────────────────────

def s2_get(client, url, params=None, retries=4, backoff=30):
    """GET from Semantic Scholar API with retry on 429."""
    for attempt in range(1, retries + 1):
        try:
            r = client.get(url, params=params, timeout=20.0)
            if r.status_code == 429:
                wait = backoff * attempt
                print(f"  S2 rate-limited (attempt {attempt}/{retries}), waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except httpx.TimeoutException:
            wait = backoff * attempt
            print(f"  S2 request timed out (attempt {attempt}/{retries}), waiting {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"S2 API failed after {retries} retries: {url}")


def fetch_author_papers(client, s2_id, limit=None):
    """Return list of paper dicts for an S2 author (all pages)."""
    papers = []
    offset = 0
    page_size = 100
    while True:
        data = s2_get(
            client,
            f"{S2_BASE}/author/{s2_id}/papers",
            params={"fields": PAPER_FIELDS, "limit": page_size, "offset": offset},
        )
        batch = data.get("data", [])
        papers.extend(batch)
        print(f"    ... fetched {len(papers)} so far", end="\r")
        if len(batch) < page_size:
            break
        offset += page_size
        time.sleep(DELAY)
        if limit and len(papers) >= limit:
            break
    print()  # newline after the \r progress
    return papers

# ── BibTeX helpers ────────────────────────────────────────────────────────────

def clean_key(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]', '', s)
    return s


def make_bibtex_key(paper):
    authors = paper.get("authors", [])
    first_last = authors[0]["name"].split()[-1] if authors else "unknown"
    year = str(paper.get("year") or "0000")
    title_words = (paper.get("title") or "untitled").split()
    title_slug = clean_key(title_words[0]) if title_words else "untitled"
    return f"{clean_key(first_last)}{year}{title_slug}"


def pub_fingerprint(paper):
    doi = (paper.get("externalIds") or {}).get("DOI", "").strip().lower()
    if doi:
        return f"doi:{doi}"
    title = (paper.get("title") or "").strip().lower()
    title = re.sub(r'\s+', ' ', title)
    return f"title:{title}"


def escape_bibtex(s):
    if s is None:
        return ""
    return str(s).replace("\\", "\\\\")


def paper_to_bibtex(paper, key):
    pub_types = paper.get("publicationTypes") or []
    venue = paper.get("venue") or ""
    journal_info = paper.get("journal") or {}
    journal_name = journal_info.get("name") or ""

    is_conf = any(t in pub_types for t in ["Conference", "ConferencePaper"])
    is_conf = is_conf or any(
        w in venue.lower()
        for w in ["conference", "proceedings", "symposium", "workshop",
                  "miccai", "isbi", "iccv", "cvpr", "neurips", "icml"]
    )
    entry_type = "inproceedings" if is_conf else "article"

    author_str = " and ".join(a["name"] for a in paper.get("authors", []))
    eids = paper.get("externalIds") or {}
    doi = eids.get("DOI", "")
    arxiv = eids.get("ArXiv", "")
    pmid = eids.get("PubMed", "")

    fields = {}
    fields["title"]    = paper.get("title", "")
    fields["author"]   = author_str
    fields["year"]     = str(paper.get("year") or "")
    fields["abstract"] = paper.get("abstract") or ""
    fields["doi"]      = doi
    if arxiv:
        fields["arxiv"] = arxiv
    if pmid:
        fields["pmid"] = pmid

    pub_date = paper.get("publicationDate") or ""
    if pub_date and len(pub_date) >= 7:
        fields["month"] = pub_date[5:7]

    if entry_type == "article":
        fields["journal"] = journal_name or venue
        vol = journal_info.get("volume") or ""
        pages = journal_info.get("pages") or ""
        if vol:
            fields["volume"] = vol
        if pages:
            fields["pages"] = pages
    else:
        fields["booktitle"] = venue

    fields["altmetric"]  = "true"
    fields["dimensions"] = "true"

    citedby = paper.get("citationCount") or 0
    if citedby:
        fields["note"] = f"Cited by {citedby}"

    pdf = (paper.get("openAccessPdf") or {}).get("url") or ""
    if pdf:
        fields["pdf"] = pdf

    lines = [f"@{entry_type}{{{key},"]
    for k, v in fields.items():
        v = v.strip() if isinstance(v, str) else str(v)
        if v:
            lines.append(f"  {k} = {{{escape_bibtex(v)}}},")
    lines.append("}")
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch Semantic Scholar pubs to BibTeX")
    parser.add_argument("--refresh", action="store_true",
                        help="Ignore cache and re-fetch everything")
    parser.add_argument("--limit", type=int, default=None, metavar="N",
                        help="Only process the N most recent pubs per author")
    parser.add_argument("--out", default=OUTPUT_FILE,
                        help=f"Output .bib file (default: {OUTPUT_FILE})")
    parser.add_argument("--cache", default=CACHE_FILE,
                        help=f"Cache file (default: {CACHE_FILE})")
    args = parser.parse_args()

    force_refresh = args.refresh
    limit = args.limit

    cache = {} if force_refresh else load_cache(args.cache)
    if force_refresh:
        print("--refresh: ignoring cache, re-fetching everything.")
    elif cache:
        print(f"Loaded cache with {len(cache)} previously fetched papers.")
    if limit:
        print(f"--limit {limit}: processing at most {limit} pubs per author.")

    seen = {}
    key_counts = {}

    with httpx.Client(headers={"User-Agent": "patchlab-bib-builder/1.0 (patchlab.pennbrain.upenn.edu)"}) as client:
        total_authors = len(AUTHORS)
        for author_idx, author in enumerate(AUTHORS):
            s2_id = author["s2_id"]
            author_name = author["name"]

            print(f"\n[{author_idx+1}/{total_authors}] Fetching {author_name} (S2={s2_id})...")

            try:
                papers = fetch_author_papers(client, s2_id, limit=limit)
            except Exception as e:
                print(f"  ERROR: {e}", file=sys.stderr)
                continue

            # Sort newest first, apply limit
            papers = sorted(papers, key=lambda p: int(p.get("year") or 0), reverse=True)
            if limit:
                papers = papers[:limit]

            print(f"  {len(papers)} papers for {author_name}")

            new_count = 0
            for i, paper in enumerate(papers):
                paper_id = paper.get("paperId", "")
                fp = pub_fingerprint(paper)

                if fp in seen:
                    continue  # silent dedup

                if paper_id and paper_id not in cache:
                    cache[paper_id] = paper
                    new_count += 1

                base_key = make_bibtex_key(paper)
                key_counts[base_key] = key_counts.get(base_key, 0) + 1
                bib_key = base_key if key_counts[base_key] == 1 else f"{base_key}{key_counts[base_key]}"

                bibtex = paper_to_bibtex(paper, bib_key)
                seen[fp] = (bib_key, bibtex)

                title_preview = (paper.get("title") or "")[:70]
                print(f"  [{i+1}/{len(papers)}] {title_preview}")

            save_cache(cache, args.cache)
            print(f"  {new_count} new, {len(papers) - new_count} already cached.")
            time.sleep(DELAY)

    print(f"\nWriting {len(seen)} entries to {args.out}...")
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("% Auto-generated by fetch_scholar.py\n")
        f.write("% Source: Semantic Scholar API (https://api.semanticscholar.org)\n")
        f.write("% Fields altmetric, dimensions added for al-folio\n\n")

        def sort_key(item):
            fp, (k, bib) = item
            m = re.search(r'year\s*=\s*\{(\d+)\}', bib)
            return (-(int(m.group(1)) if m else 0), k)

        for _, (bib_key, bibtex) in sorted(seen.items(), key=sort_key):
            f.write(bibtex)
            f.write("\n\n")

    print(f"Done. {len(seen)} unique papers -> {args.out}")


if __name__ == "__main__":
    main()
