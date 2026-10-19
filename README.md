# Apartment 14 at Heights 777

Private dossier for Horizon Growth Limited, buyer of Apartment 14: the centre residence on the fifth floor of Heights 777, Plot 777, CAD Zone A07, Parakou Street, Wuse II, Abuja.

One page, seven sheets, built on the SB2 dossier (`~/Developer/ladan-maitama-view`): welcome, the building (site plan in metres with Apartment 14 shaded, schedule, drive times), your residence (facts and a schematic front elevation with the fifth-floor bay highlighted), floor plan (Apartment 14 alone and the whole fifth floor, numbered markers), materials and specification, views, and the desk. `index.html` carries the markup, styles and interactions; `assets/` holds seven renders at 1800 px, the upper-floor plan and its crop to the centre residence.

## Editing

- Copy and figures live in `index.html`. The site plan is drawn in metres in the first IIFE after the rail (from the brochure's `buildSite()`); the elevation in the second (1 m = 4 units, cores at 11.4–14.4 and 20.2–23.2 m).
- Floor-plan markers are in `ROOMS` (percentages of each image; `unit` uses the 33–73 % crop, so x' = (x − 33) × 2.5); view text in `VIEW`.
- Contacts are in the desk sheet (Wrace International office and email, as on the SB2 dossier).
- `tools/build_assets.py` re-stages the images from the Heights 777 brochure (a local folder via `SRC`, or its GitHub Pages site) and redraws the crop; `tools/build_artifact.py <out.html>` builds the self-contained claude.ai preview.

Not hosted yet. `robots.txt` and the robots meta keep it out of search results once it is.
