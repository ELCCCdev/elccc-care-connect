import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
const port = Number(process.env.PORT || 4173);
createServer(async (req, res) => {
  if (!["/", "/index.html"].includes(new URL(req.url, "http://localhost").pathname)) {
    res.writeHead(404); res.end("Not found"); return;
  }
  try {
    const body = await readFile("index.html");
    res.writeHead(200, { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" });
    res.end(body);
  } catch { res.writeHead(404); res.end("Not found"); }
}).listen(port, "127.0.0.1", () => console.log(`Serving on http://127.0.0.1:${port}`));
