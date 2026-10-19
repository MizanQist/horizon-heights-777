# Apartment 14 at Heights 777

Private dossier for Horizon Growth Limited, buyer of Apartment 14: the centre residence on the fifth floor of Heights 777, Plot 777, CAD Zone A07, Parakou Street, Wuse II, Abuja.

One page, seven sheets, built on the SB2 dossier (`~/Developer/ladan-maitama-view`): welcome, the building (site plan in metres with Apartment 14 shaded, schedule, drive times), your residence (facts and a schematic front elevation with the fifth-floor bay highlighted), floor plan (Apartment 14 alone and the whole fifth floor, numbered markers), materials and specification, views, and the desk. `index.html` carries the markup, styles and interactions; `assets/` holds the seven renders at full source resolution (the cover is 2880 px wide), the upper-floor plan and its crop to the centre residence.

## Editing

- Copy and figures live in `index.html`. The site plan is drawn in metres in the first IIFE after the rail (from the brochure's `buildSite()`); the elevation in the second (1 m = 4 units, cores at 11.4–14.4 and 20.2–23.2 m).
- Floor-plan markers are in `ROOMS` (percentages of each image; `unit` uses the 33–73 % crop, so x' = (x − 33) × 2.5); view text in `VIEW`.
- Contacts are in the desk sheet (Wrace International office and email, as on the SB2 dossier).
- `tools/build_assets.py` re-stages the images from the Heights 777 brochure (a local folder via `SRC`, or its GitHub Pages site) and redraws the crop; `tools/build_artifact.py <out.html>` builds the self-contained claude.ai preview.

## Print edition

`apartment-14-heights-777.pdf` is a fourteen-page A4 landscape version for print (front cover, twelve pages, charcoal back cover; an even count for duplex binding), linked from the desk sheet. `python3 tools/make_pdf.py` regenerates it from `index.html` with Playwright, as in the SB2 dossier: a print stylesheet and a page cutter are injected at build time, the plan PNGs are flattened onto the panel colour, both plan views are rendered statically and the views run over two pages. No bleed or crop marks. Regenerate after editing copy or plans.

## Hosting

Live at https://mizanqist.github.io/horizon-heights-777/ from the public repo MizanQist/horizon-heights-777 (GitHub Pages, `main` at `/`; `.nojekyll` is included), with the print edition at https://mizanqist.github.io/horizon-heights-777/apartment-14-heights-777.pdf. `robots.txt` and the robots meta keep the page out of search results, but anyone with the link can open it. Edit, commit and push from `~/Developer/horizon-heights-777`: `git add -A && git -c user.name=MizanQist -c user.email=nabildeealee@icloud.com commit -m "…" && git push`; Pages rebuilds within a minute.
