import { cp, mkdir, rm, writeFile } from "node:fs/promises";

await rm("dist", { recursive: true, force: true });
await mkdir("dist", { recursive: true });
await cp("index.html", "dist/index.html");
await cp("index.html", "dist/404.html");
await cp("README.md", "dist/README.md");
await writeFile("dist/.nojekyll", "");
console.log("Built static ELCCC Care Connect prototype to dist/");
