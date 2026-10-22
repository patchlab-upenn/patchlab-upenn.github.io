#!/usr/bin/env python3
"""
Merge a freshly-fetched BibTeX file (from fetch_scholar.py) into the site's
existing publications bibliography, without silently dropping entries the
new fetch happened to miss (Semantic Scholar's API coverage varies run to run).

Entries are matched by DOI (preferred) or normalized title. For a match, the
freshly-fetched record wins (updated citation counts, fields, etc.). Entries
that exist only in the old file are kept as-is. Entries that exist only in
the new file are added. The result is sorted by year (desc), month (desc),
then first author's surname (asc) - matching the site's publications page.

Entries whose DOI is listed in excluded_dois.txt (papers Semantic Scholar wrongly
attributes to a lab author) are dropped from both files. Entries with none of
LAB_SURNAMES among their authors are listed as a warning, since they are often
such misattributions.

Usage (from the repository root):
    python3 tools/bibliography/merge_bibliography.py \
        --old _bibliography/papers.bib \
        --new tools/bibliography/merged_papers.bib \
        --out /tmp/papers_merged.bib
"""

import argparse
import os
import re

EXCLUDE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "excluded_dois.txt")

# Surnames of the authors tracked in fetch_scholar.py
LAB_SURNAMES = ["Yushkevich", "Wolk", "Das"]

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def parse_entries(path):
    text = open(path, encoding="utf-8").read()
    chunks = re.split(r"\n(?=@)", text)
    entries = []
    for c in chunks:
        c = c.strip()
        if not c.startswith("@"):
            continue
        m = re.search(r"@(\w+)\{([^,]+),", c)
        if not m:
            continue
        etype, key = m.group(1), m.group(2)
        title_m = re.search(r"title\s*=\s*\{(.*?)\}\s*,", c, re.S)
        doi_m = re.search(r"doi\s*=\s*\{(.*?)\}\s*,", c, re.S)
        title = re.sub(r"\s+", " ", title_m.group(1).strip().lower()) if title_m else ""
        doi = doi_m.group(1).strip().lower() if doi_m else ""
        fp = f"title:{title}" if title else f"doi:{doi}"
        entries.append({"key": key, "type": etype, "raw": c, "fp": fp, "doi": doi})
    return entries


def load_excluded(path):
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return {line.strip().lower() for line in f
                if line.strip() and not line.startswith("#")}


def has_lab_author(raw):
    m = re.search(r"author\s*=\s*\{(.*?)\}\s*,", raw, re.S)
    authors = m.group(1) if m else ""
    # The surname must end a name ("Sandhitsu R. Das") or start one in
    # "Last, First" form, so "E. B. B. Das Chagas" doesn't count.
    names = [n.strip() for n in re.split(r"\s+and\s+", authors)]
    return any(n.endswith(" " + surname) or n == surname or n.startswith(surname + ",")
               for n in names for surname in LAB_SURNAMES)


def first_author_surname(raw):
    m = re.search(r"author\s*=\s*\{(.*?)\}\s*,", raw, re.S)
    if not m:
        return "zzzz"
    first = re.split(r"\s+and\s+", m.group(1))[0].strip()
    if "," in first:
        last = first.split(",")[0].strip()
    else:
        parts = first.split()
        last = parts[-1] if parts else first
    return last.lower()


def get_year(raw):
    m = re.search(r"year\s*=\s*\{(\d+)\}", raw)
    return int(m.group(1)) if m else 0


def get_month(raw):
    m = re.search(r"month\s*=\s*\{([^}]*)\}", raw, re.I)
    if not m:
        return 0
    v = m.group(1).strip().lower()
    if v.isdigit():
        return int(v)
    for k, num in MONTHS.items():
        if v.startswith(k):
            return num
    return 0


def sort_key(e):
    return (-get_year(e["raw"]), -get_month(e["raw"]), first_author_surname(e["raw"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True, help="Existing site papers.bib")
    ap.add_argument("--new", required=True, help="Freshly fetched merged_papers.bib")
    ap.add_argument("--out", required=True, help="Output path")
    ap.add_argument("--exclude", default=EXCLUDE_FILE,
                    help=f"File of DOIs to drop (default: {EXCLUDE_FILE})")
    args = ap.parse_args()

    excluded = load_excluded(args.exclude)
    old = parse_entries(args.old)
    new = parse_entries(args.new)
    n_before = len(old) + len(new)
    old = [e for e in old if e["doi"] not in excluded]
    new = [e for e in new if e["doi"] not in excluded]
    n_excluded = n_before - len(old) - len(new)

    old_by_fp = {}
    for e in old:
        old_by_fp.setdefault(e["fp"], e)

    merged = {}
    for e in new:
        merged.setdefault(e["fp"], e)

    kept_from_old = 0
    for fp, e in old_by_fp.items():
        if fp not in merged:
            merged[fp] = e
            kept_from_old += 1

    entries = sorted(merged.values(), key=sort_key)

    # Guard against key collisions (rare, but two different papers could hash
    # to the same auto-generated key).
    seen = {}
    for e in entries:
        k = e["key"]
        if k in seen:
            seen[k] += 1
            new_key = f"{k}dup{seen[k]}"
            e["raw"] = e["raw"].replace(f"{{{k},", f"{{{new_key},", 1)
        else:
            seen[k] = 1

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("% Publications bibliography\n")
        f.write("% Merged via update-bibliography skill (tools/bibliography/)\n\n")
        for e in entries:
            f.write(e["raw"])
            f.write("\n\n")

    print(f"old={len(old_by_fp)} new={len(merged) - kept_from_old} "
          f"kept_from_old_only={kept_from_old} merged_total={len(entries)} "
          f"excluded={n_excluded}")
    no_lab = [e for e in entries if not has_lab_author(e["raw"])]
    if no_lab:
        print(f"WARNING: {len(no_lab)} entries have no author named "
              f"{', '.join(LAB_SURNAMES)}; check them and add misattributed DOIs "
              f"to {args.exclude}:")
        for e in no_lab:
            print(f"  {e['key']}  doi={e['doi'] or '-'}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
