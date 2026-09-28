# Design system & architecture

## Narrative

Floating navigation → atmospheric architectural hero → concise company introduction → five-category explorer → large photographic perspectives (verified projects when available) → numbered capabilities → optional verified metrics → three product families → enquiry CTA → corporate footer.

Projects receive a full-width lead image plus a staggered secondary pair. Until the attribution is verified, the section explicitly presents lighting perspectives. No false credibility counters are used.

## Visual language

- Deep Navy `#0B1E34`: navigation, capabilities and footer.
- Ivory `#F6F4EE`: editorial content, form and quiet space.
- Champagne `#C9A47A`: enquiry button, small rules and selected accents.
- Stone `#A7A29A`: dividers, neutral detail; darkened tones for readable small text.
- Charcoal `#2C2C2C`: available brand token.
- Helvetica Neue/Arial system sans stack for display and body; Georgia italic for two restrained editorial accents. No font downloads or font-induced layout shift.
- Up to 1440 px content width, responsive gutters, thin dividers, square buttons and large image crops.
- 400–850 ms controlled transitions; no scroll hijacking, carousel, parallax dependency or animation library. Reduced-motion disables transitions and smooth scrolling.

On mobile the navigation becomes a full-screen dialog, solution tabs become horizontally scrollable, project images recompose into taller crops, product families receive full-width treatments, and the enquiry drawer occupies the screen. All content remains server rendered.

## Data and interaction

`Homepage` is a singleton, with shared contact/legal fields. `Category`, `Product`, `Project`, `Capability`, and `VerifiedMetric` support a small, focused CMS. Admin uploads use Django media storage. All copy is escaped by templates; JSON-LD escapes HTML delimiters.

The enquiry dialog retains entered data after validation/network failures. Native browser validation is supplemented with Django validation, accessible server errors and an explicit keyboard focus trap. Escape, close buttons and backdrop close work; focus returns to the trigger. A no-JavaScript fallback renders the enquiry and policy content in the page, and ordinary POSTs return server-rendered errors or a redirect to the success message.

Future page links deliberately resolve to homepage sections. No dead routes or `href="#"` placeholders are used. No customer data is transmitted externally: the enquiry is stored in the configured database and reviewed in the admin.
