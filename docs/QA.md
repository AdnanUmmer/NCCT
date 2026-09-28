# QA — 28 September 2026

## Executed and passed

- Django 5.2.17 system checks: zero issues.
- All initial migrations applied to local SQLite.
- `makemigrations --check --dry-run`: no pending model changes.
- `collectstatic --noinput`: successful versioned/compressed static collection.
- `check --deploy` with production settings and a generated secret: zero issues. This checks settings, not a deployed server.
- `node --check static/js/site.js`: passed.
- **21 Django tests**, final run passing, covering homepage/schema, script escaping, idempotent seeding, publication controls, admin content access, custom 404s, required fields, email/phone validation, message limits, unknown project types, consent storage, CSRF rejection/acceptance, timing/signature/expiry, honeypot, database rate limits, forwarded-IP handling, duplicate content/replay, sanitisation, plain-HTML POST fallback, simulated storage failure, token/method handling and admin enquiry status updates.
- The test suite deliberately simulates a storage outage and logs that exception; it is an expected passing test, not a real outage.

## Browser checks

Used the Codex browser against the actual Django server at `127.0.0.1:8000`.

| Width | Horizontal overflow | Broken section anchors | Hero/CTA collision |
| --- | --- | --- | --- |
| 360 | None | None | None |
| 390 | None | None | None |
| 430 | None | None | None |
| 768 | None | None | None |
| 1024 | None | None | None |
| 1280 | None | None | None |
| 1440 | None | None | None |
| 1920 | None | None | None |

Measurements used 844 px height at phone widths and 900 px at larger widths. The browser reserves 15 px for its scrollbar. JSON evidence and full-page screenshots are in `docs/qa/`.

- Visually reviewed desktop and phone hero, solutions, product section, complete page composition, and enquiry success.
- Mobile menu opened, navigated to Products and closed correctly.
- Solution tabs switched content by mouse and arrow key.
- Empty enquiry submission focused the required Name field.
- Completed a local browser enquiry with dummy `example.test` contact details. Verified its New status, consent and Hospitality type in SQLite. The test record was removed after verification.
- Success state rendered; Escape closed the drawer and restored Enquire focus.
- Found and corrected native dialog focus wrapping. Retested Shift+Tab from close to the last link, and Tab from the last link to close; both remain inside the drawer.
- No broken image loads were reported in the DOM checks; images are locally served.
- No browser console warnings or errors recorded at the check.
- No empty `href="#"` links or nonexistent homepage anchor targets.
- Semantic landmarks, single H1, image alt text, field labels, visible focus styles and reduced-motion rules are present.

## Not measured / remaining verification

- Lighthouse Performance/Accessibility/Best Practices/SEO scores: **not run**, no numerical scores claimed.
- Production Core Web Vitals and real-world network performance: not measured. Initial hero WebP is about 149 KB desktop / 39 KB mobile; the application uses about 25 KB CSS and 7 KB JavaScript before transfer compression, with no third-party runtime fonts or libraries.
- Full WCAG 2.2 AA certification, screen-reader testing, axe audit, forced-colour mode and real Safari/Firefox/iOS/Android testing: not performed.
- PostgreSQL, load/concurrency testing, real reverse-proxy addressing, production HTTPS, media hosting and backup restoration: not exercised.
- Actual no-JavaScript browser mode was not toggled; the server-rendered form fallback is covered by Django tests and fallback CSS was inspected.
- Staff notification email and external CAPTCHA are deliberately not connected.
- Approved content/photography, legal policies and product data remain production inputs, detailed in `CONTENT-AUDIT.md`.
