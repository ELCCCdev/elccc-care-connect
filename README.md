# ELCCC Care Connect

ELCCC Client Portal, Counselor Workspace, and Administrative CRM stakeholder prototype built as a dependency-free, single-file `index.html` application using mock data only.

## Local preview

```bash
npm run dev
```

Open:

```text
http://localhost:4173/
```

## Static build

```bash
npm run build
```

The build output is written to `dist/` and is ready for static hosting.

## GitHub Pages deployment

This repository includes a GitHub Actions workflow at `.github/workflows/deploy.yml` that builds `dist/` and deploys it to GitHub Pages.

To publish publicly from GitHub:

1. Push this branch to GitHub.
2. In GitHub, open **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Open the **Actions** tab.
5. Run **Deploy static prototype to GitHub Pages** manually, or push to `main`/`work`.
6. After the workflow finishes, open the URL shown in the workflow summary. It will usually be:

```text
https://<github-username>.github.io/<repository-name>/
```

All data displayed in the prototype is mock/demo data. The app includes the disclaimer: “Prototype only — no real client or medical data.”


## Version 2: connected fictional onboarding

The deployed entry point remains `index.html`; `src/` contains the original reference modules and is not part of the static build. Existing branding, directory and filters, match quiz, resources, dashboards, profiles, demo role chooser, and presentation brief are retained. GitHub Pages configuration and build scripts are unchanged.

1. Choose **Start Demo Counseling Request** on Home, or request a booking from an existing counselor profile.
2. Select a fictional client and submit. Names are preset; no contact details or personal information are collected.
3. Open **Admin CRM**. In **Interactive Demo Onboarding**, review and mark the request contacted, assign an available counselor, then confirm a date and time.
4. Open **Counselor Dashboard** and select the assigned demo counselor to see the referral and appointment.
5. Open **Client Portal** and select the fictional request to see its status, counselor, and confirmed appointment.

The shared in-memory request collection also feeds CRM pipeline counts, appointment requests, and connected dashboard metrics. Legacy sample panels remain demonstration fixtures. New requests remain separate from existing sample client profiles. Navigation and Home are available across roles without authentication. Refreshing the page resets all new requests; no storage, network submission, medical records, authentication, or production integrations are added. Appointment times are labeled Eastern Time. Past dates and duplicate demo counselor slots are rejected; this is not a real availability service.

### Validation

Run `node scripts/check-workflow.mjs` and `npm run build`.

The dependency-free functionality check executes the actual inline application script with a lightweight DOM/event harness. It covers request submission, review, assignment, scheduling, shared role views, counselor filtering, past-date rejection, slot conflicts, existing views, and profile/role/presentation modals. The static build creates matching index/404 outputs and `.nojekyll`.

The original Version 2 checks used a lightweight DOM harness; the responsive update below adds real Chromium checks. No real data or production services are exercised.

## Responsive usability update

Navigation now follows normal document flow, with a collapsible menu at widths up to 1100px. Home and workflow role links remain visible. Containers, dashboard metrics, cards, CRM columns, tables, and forms adapt to their available width rather than requiring browser zoom changes. Headings and spacing are smaller, touch controls have a minimum 44px height, and dialog content scrolls within the viewport. The app retains all existing fictional records and workflow logic.

Keyboard support includes a skip-to-content link, visible focus indicators, current-page markers, announced menu expansion, Escape to close menus/dialogs, dialog names, focus containment, background inertness, and focus restoration. Role selection remains a demo without authentication.

### Browser validation

With the dev server running, run `node scripts/check-responsive.mjs`. This optional QA script requires Playwright in the test environment and Chromium at `/usr/bin/chromium` (override with `CHROMIUM_PATH`). The application remains dependency-free. Set `PROTOTYPE_URL` to test another local preview URL.

Verified in headless Chromium at 100% zoom: 320, 375, 390, 480, 640, 768, 1024, 1280, 1440, and 1920px widths. All seven views, expanded navigation, and five dialog types were checked for horizontal overflow. Browser controls exercised the complete fictional request, admin review, counselor assignment, appointment scheduling, counselor visibility, and updated client status at mobile width. Menu expansion/Escape and dialog keyboard focus trapping passed, without JavaScript errors. Mobile and laptop Admin screenshots were visually inspected. The existing workflow harness, static build, and whitespace checks also pass.

Testing limitations: Firefox, Safari/iOS, real touchscreen devices, on-screen keyboards, screen readers, high contrast modes, and an exhaustive WCAG audit were not tested. Viewport emulation does not substitute for those devices. New requests remain session-only, and refresh intentionally resets them. No deployment was run. The GitHub Pages workflow and build script are unchanged; the review branch is outside the existing `main`/`work` deployment triggers.
