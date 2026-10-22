---
name: update-bibliography
description: Fetch the latest publications for the PATCH Lab authors from Semantic Scholar and update the site's publications bibliography (_bibliography/papers.bib). Use when asked to update, refresh, sync, or pull in new/recent publications for the site.
---

# Update the site bibliography

Refreshes `_bibliography/papers.bib` with newly published papers, without silently
losing entries already on the site. Semantic Scholar's per-author paper listing is not
perfectly stable between runs: some previously returned papers can be missing from a
later fetch, so the fresh fetch is merged into the existing file rather than copied over
it.

All commands run from the repository root. The scripts live in `tools/bibliography/`:

- `fetch_scholar.py` fetches papers per author from the Semantic Scholar API and writes
  `tools/bibliography/merged_papers.bib`. The tracked authors are in the `AUTHORS` list
  at the top of the script (Semantic Scholar author IDs, found via
  `https://api.semanticscholar.org/graph/v1/author/search?query=<name>`; verify the ID
  by checking the author's papers before adding it).
- `merge_bibliography.py` merges that output into the site's bibliography.
- `merged_papers.bib` and `scholar_cache.json` are scratch files, ignored by git.
  Deleting them is harmless; every run re-fetches all papers.

## Steps

1. **Start a branch** as described in CLAUDE.md, and set up the Python environment once:

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r tools/bibliography/requirements.txt
   ```

2. **Back up the live file:**

   ```bash
   cp _bibliography/papers.bib /tmp/papers_bib_backup_$(date +%Y%m%d%H%M%S).bib
   ```

3. **Run the fetch for real, not a `--limit` test.** It takes a few minutes (rate
   limited to about one request per second). To test the script, write to scratch files
   with `--out /tmp/test.bib --cache /tmp/test_cache.json`.

   ```bash
   .venv/bin/python tools/bibliography/fetch_scholar.py
   ```

4. **Merge into the site bibliography:**

   ```bash
   python3 tools/bibliography/merge_bibliography.py \
     --old _bibliography/papers.bib \
     --new tools/bibliography/merged_papers.bib \
     --out /tmp/papers_merged.bib
   ```

   Read the printed counts. If `kept_from_old_only` is large, the fetch may have been
   rate limited or truncated; check the fetch output before going on. The merge sorts
   entries by year (descending), month (descending), then first author's surname. The
   publications page shows entries in file order (`sort_by` is unset in the `scholar:`
   block of `_config.yml`).

5. **Validate** with the BibTeX library jekyll-scholar uses, and check for duplicate
   titles or keys:

   ```bash
   bundle exec ruby -e 'require "bibtex"; puts BibTeX.open("/tmp/papers_merged.bib").entries.count'
   ```

6. **Install it and rebuild:**

   ```bash
   cp /tmp/papers_merged.bib _bibliography/papers.bib
   bundle exec jekyll build
   ```

7. **Spot-check locally.** Check that port 4000 is free (`lsof -i :4000 -sTCP:LISTEN`);
   if not, use another port such as 4001. Wait for `Server address` in the log (the
   first build takes a while because ImageMagick generates responsive images), then
   open `/publications/` and check the entry count and year order.

8. Report the diff stat (`git diff --stat _bibliography/papers.bib`) and how many papers
   were added, kept and updated. Then continue with the usual pull request workflow in
   CLAUDE.md.

## Known quirks

- The fetch script's BibTeX escaping only handles backslashes. A malformed title or
  abstract shows up as a Ruby parse error in step 5, which is why that step exists.
- A few entries have no parsable `year`; they sort to the bottom. That is expected.
- Some `publicationDate` values are in the future (forthcoming issues). That is expected.
- The script does not set `google_scholar_id`. al-folio's Scholar badge needs a
  per-paper Scholar citation code, which Semantic Scholar doesn't provide. Don't put an
  author's Scholar profile ID there; it produces broken badges.
