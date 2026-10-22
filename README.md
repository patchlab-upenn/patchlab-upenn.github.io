# PATCH Lab website

Source for **https://patchlab.pennbrain.upenn.edu**, the website of the Penn ADRD
Trajectories, Copathology, and Heterogeneity (PATCH) Lab at the University of
Pennsylvania. It is a Jekyll site built on the
[al-folio](https://github.com/alshedivat/al-folio) theme.

The easiest way to update the site is to ask [Claude Code](https://claude.com/claude-code)
to do it, then open a pull request. The tutorial below walks through that.

## Updating the website with Claude Code

### One-time setup

Lab members don't need write access to this repository. You work on your own copy (a
_fork_) and propose changes with a pull request, which a lab admin reviews and merges.

1. Install [Claude Code](https://docs.claude.com/en/docs/claude-code/overview), and make
   sure you have `git`, the GitHub CLI (`gh`), Ruby with Bundler, Node.js and
   ImageMagick. On a Mac, `brew install git gh ruby node imagemagick` covers all of
   these. Log in to GitHub with `gh auth login`.
2. Fork and clone the repository, then start Claude Code in it:

   ```sh
   gh repo fork patchlab-upenn/patchlab-upenn.github.io --clone
   cd patchlab-upenn.github.io
   claude
   ```

   `gh repo fork --clone` creates your fork on GitHub, clones it, and sets the lab's
   repository up as the `upstream` remote.

3. Ask Claude to get the site running locally:

   > Install what's needed and show me how to preview the site locally.

   Claude runs `bundle install` and `npm ci`, then starts `bundle exec jekyll serve`.
   Open http://localhost:4000 to see the site. It rebuilds when files change, so you can
   leave it running while you work. The first build takes a minute while ImageMagick
   generates resized images.

### Making a change

Each change follows the same loop: start a branch, describe what you want in plain
language, check the result, refine, and open a pull request.

**1. Start from a fresh branch.** Your fork doesn't update itself, so bring it up to date
with the lab's repository first:

> Sync my fork with the lab's repository and create a branch called update-my-profile.

**2. Describe the change.** Be specific and point Claude to sources. Claude can read web
pages, download images, look up papers, and edit the site files. Some examples:

- _People:_

  > Add Jane Doe to the People page as a PhD student, using her profile at
  > https://example.edu/jane. Use her photo, cropped so it's centered on her face.

  > Update my bio and photo from my Penn faculty page: https://www.med.upenn.edu/apps/faculty/...

  > Remove John Smith from the People page; he has graduated.

- _Research:_

  > Add a research project card about our new postmortem MRI atlas, with this figure
  > and a link to the paper doi:10.xxxx/yyyy.

- _News:_

  > Add a news item: Amanda Denning defended her dissertation on May 1, 2026.
  > Turn on the news section on the homepage.

- _Other pages:_

  > Post a job ad for a postdoc on the Jobs page. Here is the text: ...

  > Add our new GitHub repository pyushkevich/newtool to the Repositories page.

You can paste screenshots into Claude Code to show what looks wrong.

**3. Check the result** at http://localhost:4000, or ask Claude to take screenshots and
review them. Tell Claude what to change ("the photo is too zoomed in", "move this card
to the top") and repeat until you're happy. Check facts yourself, especially names,
roles, IDs and anything summarizing a paper.

**4. Open a pull request.** When you're done:

> Run Prettier, commit these changes and open a pull request to the lab's repository.

The repository's checks require Prettier formatting, so Claude formats the changed files
first. Claude then commits to your branch, pushes it to your fork, and opens a pull
request (PR) against `patchlab-upenn/patchlab-upenn.github.io`. Then:

- A lab admin approves the automated checks. GitHub requires this for first-time
  contributors. The checks build the site and verify formatting and links.
- The admin reviews the PR. If they ask for changes, describe them to Claude on the same
  branch and push again; the PR updates automatically.
- Once the PR is merged, the live site updates automatically within a few minutes.

For your next change, start again at step 1 so your new branch starts from the latest
version of the site.

### Tips

- **Photos** should be cropped around the face and saved without metadata (EXIF can
  include GPS location). Ask Claude to do both.
- **Figures from papers:** only reuse figures whose license allows it (for example
  CC BY), and credit them. Ask Claude to check the license.
- **Publications** are listed from `_bibliography/papers.bib`. Small fixes can be made
  there directly. To pull in new papers from Semantic Scholar, ask Claude to "update the
  bibliography". It follows the steps in `.claude/skills/update-bibliography/SKILL.md`,
  using the scripts in `tools/bibliography/`, and merges new papers into the file
  without dropping existing ones.
- **Big changes:** for something large, such as a redesign or many new pages, ask Claude
  to propose a plan first.

## For admins: reviewing pull requests

1. On a PR from a new contributor, click **Approve and run** so the checks can run.
2. Look over the **Files changed** tab. To see the result, check the PR out locally
   (`gh pr checkout <number>`, then `bundle exec jekyll serve`), or ask Claude Code to
   do it and take screenshots.
3. Ask for changes in a review comment, or merge with **Squash and merge**. The site
   deploys automatically within a few minutes.

Admins are the people with Admin or Maintain access to this repository. Everyone else
contributes through forks and needs no access.

## Where things live

| What                           | Where                                                                                                                                            |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| People page                    | `_pages/profiles.md` (one entry per person: photo, name, links) with bios in `_pages/people/people_<name>.md` and photos in `assets/img/people/` |
| Homepage text and address      | `_pages/about.md`                                                                                                                                |
| Research projects              | `_projects/<n>_<slug>.md` (`category: primary` or `adjacent`), images in `assets/img/<project>/`                                                 |
| Publications                   | `_bibliography/papers.bib`, updated with the scripts in `tools/bibliography/` (tracked authors are listed in `fetch_scholar.py`)                 |
| Software, Teaching, Jobs pages | `_pages/software.md`, `_pages/teaching.md`, `_pages/jobs.md`                                                                                     |
| GitHub repositories shown      | `_data/repositories.yml`                                                                                                                         |
| News items                     | `_news/<date>-<slug>.md` (shown on the homepage when `announcements.enabled` is `true` in `_pages/about.md`)                                     |
| Lab social links               | `_data/socials.yml`                                                                                                                              |
| Site settings                  | `_config.yml`                                                                                                                                    |
| Menu                           | `nav: true` and `nav_order:` at the top of each page in `_pages/`                                                                                |

## Running locally without Claude Code

```sh
bundle install
npm ci
bundle exec jekyll serve
```

Then open http://localhost:4000. Check formatting with `npx prettier . --check`, and fix
it with `npx prettier . --write`. Alternatively, `docker compose up` serves the site at
http://localhost:8080 without installing Ruby.

## Deployment

Pushes to `main` are built and deployed to GitHub Pages by
`.github/workflows/deploy.yml`, which publishes to the `gh-pages` branch. The `CNAME`
file points the site at `patchlab.pennbrain.upenn.edu`. Pull requests are built as a
check but not deployed.

The site is based on [al-folio](https://github.com/alshedivat/al-folio) (MIT license).
The theme's own documentation, demo pages and example content were removed from this
repository; see the al-folio repository for theme features and options.
