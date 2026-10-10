import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
const port = Number(process.env.PORT || 4173);
const types = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css" };
createServer(async (req, res) => {
  try {
    const path = normalize(req.url === "/" ? "/index.html" : req.url.split("?")[0]);
    const file = join(process.cwd(), path);
    const body = await readFile(file);
    res.writeHead(200, { "content-type": types[extname(file)] || "text/plain" });
    res.end(body);
  } catch {
    res.writeHead(404); res.end("Not found");
  }
}).listen(port, "0.0.0.0", () => console.log(`Serving on http://0.0.0.0:${port}`));
