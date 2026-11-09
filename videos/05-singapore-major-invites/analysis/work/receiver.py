"""Tiny local receiver: the HLTV tab in the built-in browser POSTs JSON here, it is saved under video05/research/hltv/."""
import http.server, json, pathlib, re

OUT = pathlib.Path(r"D:\Youtube\video05\research\hltv")
OUT.mkdir(parents=True, exist_ok=True)


class H(http.server.BaseHTTPRequestHandler):
    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "https://www.hltv.org")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(204); self.cors(); self.end_headers()

    def do_GET(self):
        # bridge page: gets {name, payload} by postMessage from the HLTV tab and POSTs it to this server
        page = b"""<!doctype html><script>
window.addEventListener('message', async (e) => {
  if (e.origin !== 'https://www.hltv.org') return;
  const r = await fetch('/' + e.data.name, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: e.data.payload});
  e.source.postMessage({saved: e.data.name, status: r.status, text: await r.text()}, e.origin);
});
</script>bridge ready"""
        self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers()
        self.wfile.write(page)

    def do_POST(self):
        name = re.sub(r"[^\w.-]", "_", self.path.strip("/")) or "data.json"
        body = self.rfile.read(int(self.headers["Content-Length"]))
        if "x-www-form-urlencoded" in (self.headers.get("Content-Type") or ""):
            from urllib.parse import parse_qs
            body = parse_qs(body.decode("utf-8"))["payload"][0].encode("utf-8")
        json.loads(body)  # must be valid JSON
        (OUT / name).write_bytes(body)
        self.send_response(200); self.cors(); self.end_headers()
        self.wfile.write(f"saved {name} {len(body)} bytes".encode())
        print("saved", name, len(body), flush=True)


http.server.HTTPServer(("127.0.0.1", 8765), H).serve_forever()
