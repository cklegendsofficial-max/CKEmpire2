#!/usr/bin/env python3
"""
Simple HTTP Server for CKEmpire
"""

import http.server
import socketserver
import json

class CKEmpireHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "CKEmpire API",
                "status": "running",
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    PORT = 8011
    with socketserver.TCPServer(("", PORT), CKEmpireHandler) as httpd:
        print(f"🚀 Starting CKEmpire HTTP Server on port {PORT}")
        print(f"📍 URL: http://localhost:{PORT}")
        httpd.serve_forever() 