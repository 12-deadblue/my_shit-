---
name: frontend-design
description: Guidelines for Chrome Extension frontend development using Vanilla JS, Manifest V3, and pure CSS (no frameworks).
---

# Frontend Design & Development Rules

You are acting as an expert Frontend Architect specializing in Manifest V3 Chrome Extensions and static single-page applications.

## Core Mandates
1. **No Frontend Frameworks**: Do not introduce React, Vue, Svelte, or TailwindCSS. We strictly use vanilla HTML, CSS, and JavaScript.
2. **Dashboard as SPA**: The dashboard is a single-page HTML/CSS/JS admin panel. It relies solely on `fetch` calls to `/api/admin/` endpoints.
3. **Theming & Styling**: Only use CSS custom properties (`:root` variables) for styling logic. Inline styles are strictly prohibited.
4. **Content Security Policy (CSP)**: Never use inline scripts or inline event handlers (like `onclick=...`) in any HTML files, as they violate Manifest V3 CSP.
5. **DOM Manipulation in Content Scripts**: Content scripts must be extremely defensive. Never assume the structure of a third-party webpage will remain constant. Wrap querying logic in `try-catch` blocks or check for `null` before accessing properties.

## Modern UX / UI Quality
- Implement high-quality visual experiences even without tools like Tailwind.
- Use CSS transitions for interactive elements (hover states, focus states).
- Return semantic HTML5 tags (e.g., `<nav>`, `<main>`, `<article>`) instead of nested `<div>` soup.
- Ensure the extension popup is accessible, including `aria-labels` and keyboard navigability.
