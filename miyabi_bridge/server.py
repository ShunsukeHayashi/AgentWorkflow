import http.server
import socketserver
import json
import os
from pathlib import Path

PORT = 8989
JOB_FILE = "miyabi_bridge/job.json"

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(CORSRequestHandler, self).end_headers()

    def do_GET(self):
        if self.path == '/latest_job':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if os.path.exists(JOB_FILE):
                with open(JOB_FILE, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(json.dumps({"error": "No job found"}).encode())
        else:
            # Fallback to serving files (images, etc)
            return super().do_GET()

print(f"🌉 Miyabi Bridge Server active at http://localhost:{PORT}")
print("Waiting for Chrome Extension requests...")

with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
    httpd.serve_forever()
