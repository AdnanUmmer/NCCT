# Application navigation, chevrons and product image presentation

## Verified application destinations

- Residential: /applications/residential-lighting/
- Offices/commercial: /applications/office-commercial-lighting/
- Hospitality: /applications/hospitality-lighting/
- Retail/display: /applications/retail-display-lighting/
- Exterior/landscape: /applications/exterior-landscape-lighting/
- Public/circulation: /applications/public-circulation-lighting/
- Industrial/warehouse: /applications/industrial-warehouse-lighting/

Each page has distinct introductory guidance, environments and considerations, real published categories, relevant solution links and verified published products. Existing nine solution records and URLs remain intact. The Solutions explorer retains separate links to the relevant solution and the new application guide. No database changes or migrations.

## Changed files

- core/application_content.py: seven distinct editorial application profiles.
- core/editorial.py: application-specific links with separate solution URLs.
- core/catalogue.py: application detail view and explorer relationships.
- config/urls.py and core/sitemaps.py: application routes and sitemap entries.
- templates/catalogue/application.html: new application detail presentation.
- templates/catalogue/solutions.html: separate application guide links and SVG chevrons.
- templates/partials/chevron.html: shared decorative currentColor SVG.
- templates/sections/application_card.html and templates/home.html: replace decorative Unicode arrows without layout redesign.
- templates/base.html and static/css/product-presentation.css: shared chevron movement and neutral product-only image surfaces, contain sizing and consistent padding.
- products/models.py and products/presentation.py: reviewed variant selection with original/upload fallback and source-checksum invalidation; no schema changes.
- products/image_variants.json and static/images/products-isolated/*.png: nine reviewed transparent variants, saved separately.
- docs/PRODUCT-IMAGE-REVIEW.json: all 61 image decisions, including manual-review items.
- core/test_application_navigation.py: destination, vector-chevron and uploaded-replacement regression coverage.

## Product background status

Nine isolated products have approved transparent variants. Source RGB pixels and dimensions are byte-for-byte preserved; only connected near-white background alpha is removed. Original files are unchanged. Thirty-five environmental/illuminated images retain their original backgrounds. Seventeen delicate or low-contrast isolated products remain flagged for manual review. Background cleanup is therefore partial: retained originals can still show their original background within the consistent neutral product container. No product was regenerated.

## Verification

Django check passed; no migrations detected. 31 catalogue/editorial/CMS regression tests and 3 new application tests passed. All seven application cards individually tested on desktop and mobile, with no redirects, broken image loads or horizontal overflow. All nine solutions preserved. Product detail and catalogue variants and object-fit containment checked. Screenshots reviewed in installed Edge at 1366px and 390px. Decorative Unicode link arrows no longer occur in templates. No physical iOS/Safari test environment was available; iOS rendering has not been claimed.

Evidence: C:/Users/10adn/OneDrive/Documents/New project/ncct-navigation-products/

No Git push or deployment performed.
