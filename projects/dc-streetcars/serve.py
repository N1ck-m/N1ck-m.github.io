# Local dev server for the dc-streetcars app: static files + POST /save for browser->disk exports.
# Localhost-only, path-sanitized. Not for production use.
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == '/save':
            q = urllib.parse.parse_qs(u.query)
            rel = q.get('path', [''])[0]
            rel = os.path.normpath(rel).lstrip('/\\')
            if not rel or '..' in rel.split(os.sep):
                self.send_response(403); self.end_headers(); return
            n = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(n)
            p = os.path.join(ROOT, rel)
            d = os.path.dirname(p)
            if d: os.makedirs(d, exist_ok=True)
            with open(p, 'wb') as f:
                f.write(data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(len(data)).encode())
            return
        self.send_response(404); self.end_headers()

    def log_message(self, *a):
        pass

if __name__ == '__main__':
    os.chdir(ROOT)
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
