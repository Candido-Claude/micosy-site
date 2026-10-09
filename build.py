#!/usr/bin/env python3
"""Build the public Mi.COSY site from the template, the nine portfolio works and the works added on the team page.

Inputs (all optional except the template):
  data/works/<id>.json       documents of the team page's `works` collection (ArtifactData out_dir format)
  data/overrides/<key>.json  documents of its `overrides` collection (edits/hiding of the nine portfolio works)
  data/assets/<assetId>.*    images of the added works, as saved by the Artifact tool's asset read
Output: docs/ (index.html + img/ + CNAME), served by GitHub Pages at micosy.eu.
"""
import glob
import html
import json
import os
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "template.html")
DATA = os.path.join(ROOT, "data")
SITE = os.path.join(ROOT, "docs")
BASE_IMG = os.path.join(ROOT, "base-img")

STATIC = [
    ("s0", "w1-pink-panther", "The Pink Panther show", "118 × 150 cm", "Acrylic",
     "Cosy on a stage with red curtains next to the Pink Panther and a crowd of cartoon friends; a sign reads The Pink Panther show."),
    ("s1", "w2-ducks", "Don't hit the Ducks", "120 × 100 cm", "Acrylic",
     "Cosy in a red coat holding a slingshot, ducks and a target on blue and white stripes; a sign reads Don't hit the duck."),
    ("s2", "w3-farmers", "The Farmers", "100 × 100 cm", "Acrylic",
     "Three hooded figures with orange faces standing in black and white striped fields under a blue wavy sky."),
    ("s3", "w4-lady", "Mi Cosy Lady", "80 × 80 cm", "Acrylic",
     "Cosy as a lady with long pink hair and a pink striped top, carrying a Be Cosy bag, on red and white stripes."),
    ("s4", "w5-cosys", "Creative, money, peaceful cosys", "100 × 100 cm", "Acrylic, textile",
     "Three Cosy heads in blue, green and pink, painted above real shirt collars sewn onto the canvas."),
    ("s5", "w6-serviette", "Cosy holding a serviette", "70 × 70 cm", "Acrylic, textile",
     "Cosy in a red striped top on diagonal red and white stripes, holding a real checkered cloth that hangs off the canvas."),
    ("s6", "w7-stitches", "Cosy stitches", "60 × 60 cm", "Acrylic, textile, oil pastel",
     "A purple-faced Cosy wearing a real denim shirt stitched onto the canvas, with Be cosy lettering on green stripes."),
    ("s7", "w8-cheesecake", "Cheesecake tasting", "80 × 80 cm", "Acrylic",
     "Cosy with a fork, tongue out, in front of a slice of cheesecake on a plate, on blue stripes."),
    ("s8", "w9-melting-ice", "Melting ice", "70 × 70 cm", "Acrylic",
     "Cosy with a blue mosaic head holding a dripping red ice lolly, on yellow and white stripes."),
]


def load_docs(collection):
    """Return {doc_id: fields} for every JSON file saved under data/<collection>/."""
    docs = {}
    for path in sorted(glob.glob(os.path.join(DATA, collection, "*.json"))):
        try:
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, ValueError) as e:
            print(f"skip {path}: {e}", file=sys.stderr)
            continue
        fields = raw.get("data") if isinstance(raw, dict) and isinstance(raw.get("data"), dict) else raw
        if isinstance(fields, dict):
            docs[os.path.splitext(os.path.basename(path))[0]] = fields
    return docs


def fmt_price(p):
    try:
        return "€ " + f"{int(round(float(p))):,}".replace(",", " ")
    except (TypeError, ValueError):
        return ""


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def find_asset(asset_id):
    for path in glob.glob(os.path.join(DATA, "assets", asset_id + ".*")):
        return path
    return None


def prepare_upload(asset_id, src_path):
    """Copy an added work's image into site/img/uploads as a web-sized image plus a thumbnail."""
    out_dir = os.path.join(SITE, "img", "uploads")
    os.makedirs(out_dir, exist_ok=True)
    full = os.path.join(out_dir, asset_id + ".webp")
    thumb = os.path.join(out_dir, asset_id + "-s.webp")
    if not (os.path.exists(full) and os.path.exists(thumb)):
        im = Image.open(src_path).convert("RGB")
        big = im.copy(); big.thumbnail((1400, 1400), Image.LANCZOS); big.save(full, "WEBP", quality=84, method=6)
        small = im.copy(); small.thumbnail((640, 640), Image.LANCZOS); small.save(thumb, "WEBP", quality=80, method=6)
    w, h = Image.open(thumb).size
    return "img/uploads/" + asset_id + ".webp", "img/uploads/" + asset_id + "-s.webp", w, h


def figure_html(i, w):
    cap = [f'<span class="pill">Title: {esc(w["title"])}</span>']
    meta = f'Size: {esc(w["size"] or "—")}<small>Technique: {esc(w["tech"] or "—")}{" · " + esc(w["year"]) if w["year"] else ""}</small>'
    cap.append(f"<span>{meta}</span>")
    if w["status"] == "available":
        price = fmt_price(w["price"]) if w["price"] else ""
        cap.append(f'<span class="pill pill--status pill--available">Available{" · " + price if price else ""}</span>')
    elif w["status"] == "sold":
        cap.append('<span class="pill pill--status pill--sold">Sold</span>')
    dims = f' width="{w["tw"]}" height="{w["th"]}"' if w.get("tw") else ""
    return (
        '        <figure class="work">\n'
        f'          <figcaption>{"".join(cap)}</figcaption>\n'
        f'          <button class="work__btn" type="button" data-i="{i}" aria-label="Open {esc(w["title"])}">\n'
        f'            <img src="{esc(w["thumb"])}"{dims} loading="lazy" alt="{esc(w["alt"])}">\n'
        "          </button>\n"
        "        </figure>"
    )


def main():
    os.makedirs(SITE, exist_ok=True)
    # base images (portfolio works, wordmark, textures)
    img_out = os.path.join(SITE, "img")
    os.makedirs(img_out, exist_ok=True)
    for path in glob.glob(os.path.join(BASE_IMG, "*")):
        if os.path.isfile(path):
            shutil.copy2(path, img_out)

    works_docs = load_docs("works")
    overrides = load_docs("overrides")
    items = []

    # works added on the team page, newest first
    added = []
    for doc_id, d in works_docs.items():
        asset_id = str(d.get("assetId") or "")
        src_path = find_asset(asset_id) if asset_id else None
        if not src_path:
            print(f"work {doc_id}: image {asset_id or '(none)'} not downloaded yet, skipped", file=sys.stderr)
            continue
        full, thumb, tw, th = prepare_upload(asset_id, src_path)
        added.append({
            "created": str(d.get("createdAt") or ""),
            "src": full, "thumb": thumb, "tw": tw, "th": th,
            "title": str(d.get("title") or "Untitled"), "size": str(d.get("size") or ""), "tech": str(d.get("technique") or ""),
            "year": str(d.get("year") or ""), "status": d.get("status") if d.get("status") in ("available", "sold") else "",
            "price": d.get("price") if isinstance(d.get("price"), (int, float)) else None,
            "alt": str(d.get("title") or "Untitled") + " by Mi.COSY",
        })
    added.sort(key=lambda w: w["created"], reverse=True)
    items.extend(added)

    # the nine portfolio works, with any edits made on the team page
    for key, stem, title, size, tech, alt in STATIC:
        o = overrides.get(key, {})
        if o.get("hidden"):
            continue
        tw, th = Image.open(os.path.join(BASE_IMG, stem + "-s.webp")).size
        items.append({
            "src": f"img/{stem}.webp", "thumb": f"img/{stem}-s.webp", "tw": tw, "th": th,
            "title": str(o.get("title") or title), "size": str(o["size"]) if o.get("size") is not None else size,
            "tech": str(o["technique"]) if o.get("technique") is not None else tech,
            "year": str(o.get("year") or ""), "status": o.get("status") if o.get("status") in ("available", "sold") else "",
            "price": o.get("price") if isinstance(o.get("price"), (int, float)) else None, "alt": alt,
        })

    grid = "\n".join(figure_html(i, w) for i, w in enumerate(items))
    works_json = json.dumps([{"src": w["src"], "title": w["title"], "size": w["size"], "tech": w["tech"], "year": w["year"], "alt": w["alt"]} for w in items], ensure_ascii=False)
    count = f"{len(items)} works · acrylic, textile and oil pastel"

    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    page = page.replace("{{WORKS}}", grid).replace("{{COUNT}}", esc(count)).replace("{{WORKS_JSON}}", works_json.replace("</", "<\\/"))
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    with open(os.path.join(SITE, ".nojekyll"), "w") as f:
        f.write("")
    with open(os.path.join(SITE, "CNAME"), "w") as f:
        f.write("micosy.eu\n")
    print(f"site built: {len(items)} works ({len(added)} added on the team page), {sum(1 for _ in glob.glob(os.path.join(img_out, '*')))} images")


if __name__ == "__main__":
    main()
