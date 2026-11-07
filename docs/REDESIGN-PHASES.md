# Redesign phases — 2 November 2026

## Phase 1: Stabilise the content-led foundation (complete)
- Reused prior route, asset and source audit; no database migrations or production changes.
- Collected the new editorial stylesheet required by manifest storage.
- Restored the administrator-controlled About image.
- Reused category query results between the catalogue and footer.
- Kept active-category accessibility and styling markers with the new sidebar.
- Django suite: 66 tests pass. Includes CMS, filters, guides, downloads and enquiry backend coverage.

## Next implementation phases
2. Homepage and shared visual refinement: full-screen hero, restrained luminaire-inspired navbar, category product visuals and three reference cards in a desktop row. Preserve the latest brief's balanced image/content direction.
3. Inner-page refinement: consistent three-column project images, selective solution imagery, one About visual and polished resource presentation.
4. Browser QA at 360, 390, 768, 1024, 1366 and 1440px, including actual desktop/mobile screenshots, filters and inline enquiry interactions.

## Content boundaries
Existing product records and source-attributed datasheets remain authoritative. General lighting guides are editorial content, not product specifications. Original-site patent, flexible-system and manufacturer claims remain unverified as NCCT-owned capabilities. Existing source inventory and CONTENT-AUDIT.md document that distinction. Proposed vision/mission copy needs owner review.

No deployment, push or production data changes performed. Visual completion is not claimed by the unit tests.

## Phase 2 completed
- Full-height desktop hero; compact mobile composition.
- Restrained dark floating navigation with a thin warm diffuser line; simplified on mobile.
- Existing category images and three database-backed reference cards in one desktop row.
- 66 Django tests passed. Browser checks at all six requested widths found no horizontal overflow. Desktop/mobile hero and reference screenshots inspected.
- Existing reference imagery and descriptions appear inconsistent in some records (for example an urban panorama with a garden-lighting description). Preserve admin records; review image/copy pairing before publication rather than inventing attribution.
- Preview available at http://127.0.0.1:8022/. No production deployment or data changes.
