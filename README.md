# ELCCC Care Connect

ELCCC Client Portal, Counselor Workspace, and Administrative CRM stakeholder prototype built as a dependency-free, single-file `index.html` application using mock data only.

## Application source of truth

`index.html` is the only application source in this repository and the exact artifact produced by the build. Its HTML, CSS, JavaScript, and mock data are embedded in that file. The build does not compile or bundle a separate application source tree.

Future application changes should be made in `index.html`. If the project later migrates to modular source files or a framework, update the build, documentation, and deployment checks together so there is still one unambiguous deployable source.

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

This repository includes a manually triggered GitHub Actions workflow at `.github/workflows/deploy.yml` that builds `dist/` and deploys it to GitHub Pages. Merging a pull request does **not** automatically replace the currently published site.

To publish publicly from GitHub:

1. Before deployment, compare `index.html` on the selected commit with the currently published application and obtain stakeholder approval.
2. In GitHub, open **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Open the **Actions** tab.
5. Run **Deploy static prototype to GitHub Pages** manually from the approved commit. Select `main` only after the preservation review is complete.
6. After the workflow finishes, open the URL shown in the workflow summary. It will usually be:

```text
https://<github-username>.github.io/<repository-name>/
```

All data displayed in the prototype is mock/demo data. The app includes the disclaimer: “Prototype only — no real client or medical data.”
