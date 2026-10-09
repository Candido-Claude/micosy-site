# Mi.COSY public site — how it is updated

The public site (micosy.eu) is a static copy of what visitors see on the Mi.COSY team page on claude.ai.
The team page is the back-office: the team signs in there to add, edit or remove works. This repository
turns that data into the public site.

Team page: https://claude.ai/artifact/SDJcj6nio129G6ArxZJpDD

## Layout

- `template.html` — the public page, with `{{WORKS}}`, `{{COUNT}}` and `{{WORKS_JSON}}` placeholders.
- `base-img/` — the nine portfolio works, the wordmark, the hand-written rule titles and the textures.
- `data/works/*.json` — documents of the team page's `works` collection (works added on the page).
- `data/overrides/*.json` — documents of its `overrides` collection (edits or hiding of the nine portfolio works).
- `data/assets/<assetId>.<ext>` — the images of the added works, downloaded from the team page.
- `build.py` — builds `docs/` from the above.
- `docs/` — the generated site, served by GitHub Pages (custom domain in `docs/CNAME`).

## Sync procedure (run by Claude, daily or on request)

1. Read the team page's data with the ArtifactData tool, saving the documents as files:
   - `list` collection `works`, `out_dir` = `<repo>/data`
   - `list` collection `overrides`, `out_dir` = `<repo>/data`
   Remove from `data/works/` any JSON file whose document no longer exists (the work was removed on the page).
2. For every work whose `assetId` has no file yet under `data/assets/`, download the image with the Artifact
   tool: `read`, `url` = team page, `path` = the asset id, `out_dir` = `<repo>/data/assets`.
3. Run `python3 build.py` (needs Pillow).
4. If `git status` shows changes: commit (`Sync works from the team page`) and push to `main`.
   GitHub Pages redeploys micosy.eu within a minute or two.

Nothing in this repository holds a password: the team sign-in lives on the team page only.
