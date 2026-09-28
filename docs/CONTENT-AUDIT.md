# Content & asset audit — 28 September 2026

## Received

Only `Pasted text.txt` was attached. No new identity image, vector logo, Figma file, PDF concept, project schedule, product datasheet or photography pack was supplied. The palette and “People · Places · Progress” direction come directly from the written brief.

The unrelated `document-extraction` workspace was left untouched. A separate `ncct` directory contains this implementation.

## Source findings

| Source | Safely reusable material | Treatment |
| --- | --- | --- |
| https://ncctdxb.com/en/index.html | Five named lighting categories; LED/personalised lighting discussion; Dubai address, phone and email; existing scene imagery | Concise rewritten copy, locally stored imagery and contact details |
| https://ncctdxb.com/en/contact-2/index.html | info@ncctdxb.com, +971 58 1310300, Office 2202, Ubora Tower, Al Abraj Street, Business Bay | These consistent details are used; malformed phone suffix omitted |
| https://ncctdxb.com/en/Real/indoor_lights.html | Indoor product images, category names | Ceiling/wall family descriptions based on visible images; no model/specification invented |
| https://ncctdxb.com/en/Real/Outdoor_lights.html | Outdoor category | Retain category; exact case matters in URL |
| https://ncctdxb.com/en/Real/Decorative_lights.html | Decorative category | Retain category; exact case matters in URL |
| https://ncctdxb.com/en/Real/industrial_lights.html | Industrial category and pendant image | Family preview, no performance claims |
| https://ncctdxb.com/en/Real/professional_lights.html | Professional category and equipment images | Category explorer only |

Source HTML snapshots and `assets.json` are included for traceability. Utilities download only explicit linked image assets. The runtime makes no requests to these source websites.

## Conflicts and omissions

1. The homepage project captions name Rzeszow, Milan and Szczecin, use wording such as “could”, and their image URLs resolve to fixtures/garden lighting. The fallback building-image URLs return 404. These cannot substantiate completed NCCT projects or location metadata. No such project names, clients or delivery claims are published.
2. Existing hero images depict interior/exterior lighting scenes without reliable location, photographer or delivery attribution. They are presented as NCCT website imagery with unverified credits, not completed installations. The gallery's editorial scene titles describe the image; they are not invented project names.
3. Existing source logos are small raster files. The actual source logo is retained alongside a typeset NCCT DXB identifier; this is not presented as a newly approved logo. A new high-resolution identity asset is still needed.
4. Contact pages disagree on `sales@` versus `sales1@`; only the consistent `info@ncctdxb.com` address is used.
5. Unsubstantiated patent, market uniqueness, client, partnership, certification, international reach and experience claims are omitted.
6. No verified metrics were found. The metric model and conditional section exist, but no business numbers or counters are invented.
7. Product filenames identify category items, not models. Preview titles are plain descriptions of visible families, not product model names. Product specifications remain empty.

## Reference study

- **LuxeLED** — https://www.luxeled.com/: product discovery and named project presentation establish a clear products → work narrative. Adopted separation of products/projects, not its layout or content.
- **Thorn** — https://www.thornlighting.com/en: organised indoor/outdoor/controls discovery, case-study context and technical information. Web extraction returned 403; the browser successfully exposed the page and its navigation. Adopted application-led grouping and specifier access.
- **Zumtobel Group** — https://z.lighting/en/group/company/: large photographic editorial frame, direct hierarchy and restrained corporate navigation. Visually inspected in the browser. Adopted scale, whitespace and corporate clarity without borrowing credentials or page design.

## Required before public launch

- Supplied/new identity image, approved vector logo and any licensed font files.
- Figma/PDF references mentioned in the brief, for a subsequent comparison pass.
- Three or more confirmed NCCT projects: exact title, location, sector, scope, completion status, approved photography and usage rights.
- Confirmation of rights for all imagery currently reused from NCCT's public site, or replacements with approved project photographs.
- Approved hero image (ideally at least 2000 px wide) and mobile crop. Current hero is 1600 × 914 from NCCT.
- Current product family/model names, isolated packshots, catalogue PDF and technical data sheets. Existing images are modest-resolution catalogue graphics.
- Verified company overview and capabilities, plus documentary evidence for any desired metrics.
- Approved privacy/terms/cookie copy and enquiry retention policy. Current dialogs explicitly mark missing legal copy; they are development notices, not legal advice or approved policies.
- Production domain/hosting/database/media settings, staff access and optional notification delivery configuration.
