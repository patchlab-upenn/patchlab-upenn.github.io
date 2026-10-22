# PATCH Lab website: notes for Claude Code

Jekyll site on the al-folio theme, deployed to GitHub Pages from `main` by
`.github/workflows/deploy.yml`. See README.md for where content lives.

## Workflow

- Lab members work in a fork (`origin`) of `patchlab-upenn/patchlab-upenn.github.io`
  (`upstream`). Before starting a change, bring the fork up to date (`git fetch upstream`,
  `git checkout main`, `git merge --ff-only upstream/main`, `git push origin main`) and
  create a branch from it. Never commit to `main`. Admins working in a clone of the lab's
  repository have no `upstream`; for them `origin` is the lab's repository. Note that
  this clone may also have an `upstream` remote pointing at `alshedivat/al-folio`; don't
  sync from that unless asked to update the theme.
- When the user is done, run Prettier, commit, push the branch to the fork, and open a
  pull request to the lab's repository with
  `gh pr create --repo patchlab-upenn/patchlab-upenn.github.io`. There are no preview
  links; the user previews locally.
- Preview locally with `bundle exec jekyll serve` (http://localhost:4000). Check whether
  port 4000 is already in use first. The first build is slow because ImageMagick
  generates responsive images.
- CI requires Prettier formatting. Install the pinned versions with `npm ci`, then run
  `npx prettier --write <changed files>` and `npx prettier . --check`.
- To check a page visually, take a headless Chrome screenshot and look at it.

## Content conventions

- People: add an entry to the `profiles:` list in `_pages/profiles.md` (image under
  `assets/img/people/`, bio under `_pages/people/people_<name>.md`, links in `more_info`).
- Photos: crop around the face and re-save without EXIF metadata, which can include GPS
  location.
- Verify IDs before using them (ORCID via the ORCID API, etc.). IDs copied from other
  web pages have been wrong before.
- Research projects: `_projects/<n>_<slug>.md` with `category: primary` or `adjacent`
  (only these categories are shown). Write only from the papers' abstracts; don't add
  claims they don't support.
- Figures from papers: reuse only when the license allows it (check Crossref or Europe
  PMC), and credit the figure and license in the caption.
- News: `_news/<date>-<slug>.md`. The homepage news list is off
  (`announcements.enabled: false` in `_pages/about.md`) until there are news items.
- Publications: `_bibliography/papers.bib`. Bulk updates come from a Semantic Scholar
  fetch script that a maintainer runs outside this repository; don't regenerate the file
  wholesale.
